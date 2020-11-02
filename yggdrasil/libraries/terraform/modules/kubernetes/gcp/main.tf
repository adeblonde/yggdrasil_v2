# GKE cluster
resource "google_container_cluster" "k8s_cluster" {
  name = format("%s_%s_k8s_cluster", var.module_prefix, var.k8s_cluster_name)
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  master_auth {
    username = var.gke_username
    password = var.gke_password

    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

# Separately Managed Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = format("%s_%s_k8s_cluster", var.module_prefix, var.k8s_cluster_name)
  location   = var.region
  cluster    = google_container_cluster.k8s_cluster.name
  node_count = var.gke_num_nodes

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    labels = {
      env = var.project_id
    }

    # preemptible  = true
    machine_type = "n1-standard-1"
    tags         = ["gke-node", "${var.project_id}-gke"]
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}

############
# Security Group / Firewall group
############

resource "aws_security_group" "security_group_node" {
	
	name = format("%s_%s_sg", var.module_prefix, var.k8s_cluster_name)
	description = var.description
	vpc_id = var.network_ids[var.network_name]
	revoke_rules_on_delete = true

	dynamic "ingress" {
		for_each = var.ingress_rules

		content {
			description = ingress.value.description
			from_port = ingress.value.from_port
			to_port = ingress.value.to_port
			protocol = ingress.value.protocol
			cidr = ingress.value.cidr
		}
	}

	dynamic "egress" {
		for_each = var.egress_rules

		content {
			description = egress.value.description
			from_port = egress.value.from_port
			to_port = egress.value.to_port
			protocol = egress.value.protocol
			cidr = egress.value.cidr
		}
	}

	tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_firewall", var.module_prefix, var.k8s_cluster_name)
        }
    )
}

############
# Kubernetes Cluster
############

resource "aws_eks_cluster" "k8s_cluster" {

    name = format("%s_%s_k8s_cluster", var.module_prefix, var.k8s_cluster_name)

    role_arn = aws_iam_role.k8s_role.arn

    vpc_config = {
        subnet_ids = [for subnet_name in var.k8s_cluster_subnets : var.subnet_ids[subnet_name]]
        security_group_ids = [aws_security_group.security_group_node.id]
        endpoint_private_access = true
    } 

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_k8s_cluster", var.module_prefix, var.k8s_cluster_name)
        }
    )

}

############
# Node groups
############

resource "aws_eks_node_group" "k8s_node_groups" {

    for_each = var.k8s_node_groups

    cluster_name = format("%s_%s_k8s_cluster", var.module_prefix, var.k8s_cluster_name)
    node_group_name = format("%s_%s_%s_k8s_node_group", var.module_prefix, each.key, var.k8s_cluster_name)
    node_role_arn = aws_iam_role.k8s_role_node_group.arn
    subnet_ids = [for subnet_name in each.value.k8s_cluster_subnets : var.subnet_ids[subnet_name]]
    remote_access {
        ec2_ssh_key = format("%s_%s_%s_k8s_ssh_key", var.module_prefix, var.k8s_cluster_name, each.key)
    }

    scaling_config {
        desired_size = each.value.desired_size
        max_size = each.value.max_size
        min_size = each.value.min_size
    }

    depends_on = [aws_eks_cluster.k8s_cluster]

    ami_type = var.system_image
    instance_types = [var.instance_type]
    disk_size = var.disk_size

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_%s_k8s_node_group", var.module_prefix, var.k8s_cluster_name, each.key)
        }
    )

}

############
# Role for K8s cluster
############

resource "aws_iam_role" "k8s_role" {

    name = format("%s_%s_k8s_cluster_role", var.module_prefix, var.k8s_cluster_name)

    assume_role_policy = <<POLICY
{
    "Version": "2012-10-17"
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "eks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
POLICY
}

############
# Role for K8s cluster node groupe
############

resource "aws_iam_role" "k8s_role_node_group" {

    name = format("%s_%s_k8s_cluster_role_node_group", var.module_prefix, var.k8s_cluster_name)

    assume_role_policy = <<POLICY
{
    "Version": "2012-10-17"
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
POLICY
}

############
# Role policies
############

resource "aws_iam_role_policy_attachment" "k8s_cluster_policy" {

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
    role = aws_iam_role.k8s_role.name
}

resource "aws_iam_role_policy_attachment" "k8s_service_policy" {

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
    role = aws_iam_role.k8s_role.name
}

resource "aws_iam_role_policy_attachment" "k8s_worker_node_policy" {

    for_each = var.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
    role = aws_iam_role.k8s_role_node_group[each.value].name
}

resource "aws_iam_role_policy_attachment" "k8s_cni_policy" {

    for_each = var.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
    role = aws_iam_role.k8s_role_node_group[each.value].name
}

resource "aws_iam_role_policy_attachment" "k8s_container_registry_policy" {

    for_each = var.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    role = aws_iam_role.k8s_role_node_group[each.value].name
}
