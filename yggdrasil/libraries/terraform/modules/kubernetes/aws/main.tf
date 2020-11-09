############
# Security Group / Firewall group
############

data "aws_vpc" "k8s_vpc" {
	filter {
		name = "tag:name"
		values = [format("%s_%s_network", var.k8s_cluster.module_prefix, var.k8s_cluster.network)]
	}
}

resource "aws_security_group" "security_group_node" {
	
	name = format("%s_%s_sg", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
	description = "Kubernetes cluster" #var.k8s_cluster.description
	vpc_id = data.aws_vpc.k8s_vpc.id
	revoke_rules_on_delete = true

	dynamic "ingress" {
		for_each = var.k8s_cluster.ingress_rules

		content {
			description = ingress.value.description
			from_port = ingress.value.from_port
			to_port = ingress.value.to_port
			protocol = ingress.value.protocol
			cidr_blocks = ingress.value.cidr
		}
	}

	dynamic "egress" {
		for_each = var.k8s_cluster.egress_rules

		content {
			description = egress.value.description
			from_port = egress.value.from_port
			to_port = egress.value.to_port
			protocol = egress.value.protocol
			cidr_blocks = egress.value.cidr
		}
	}

	tags = merge(
        var.k8s_cluster.module_labels,
        {
            "name" = format("%s_%s_firewall", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
        }
    )
}

############
# Kubernetes Cluster
############

data "aws_subnet_ids" "k8s_subnet_ids" {

	vpc_id = data.aws_vpc.k8s_vpc.id
	filter {
		name = "tag:name"
		values = [for private_subnet in var.k8s_cluster.subnetworks : format("%s_%s_%s_private_subnet", var.k8s_cluster.module_prefix, var.k8s_cluster.network, private_subnet)]
	}
}

resource "aws_eks_cluster" "k8s_cluster" {

    name = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)

    role_arn = aws_iam_role.k8s_role.arn

    vpc_config {
        subnet_ids = data.aws_subnet_ids.k8s_subnet_ids.ids
        security_group_ids = [aws_security_group.security_group_node.id]
        endpoint_private_access = true
    } 

    tags = merge(
        var.k8s_cluster.module_labels,
        {
            "name" = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
        }
    )

}

############
# Node groups
############

resource "aws_eks_node_group" "k8s_node_groups" {

    for_each = var.k8s_cluster.k8s_node_groups

    cluster_name = format("%s_%s_k8s_cluster", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)
    node_group_name = format("%s_%s_%s_k8s_node_group", var.k8s_cluster.module_prefix, each.key, var.k8s_cluster.cluster_name)
    node_role_arn = aws_iam_role.k8s_role_node_group.arn
    subnet_ids = [aws_security_group.security_group_node.id]
    remote_access {
        ec2_ssh_key = format("%s_%s_%s_k8s_ssh_key", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name, each.key)
    }

    scaling_config {
        desired_size = each.value.desired_size
        max_size = each.value.max_size
        min_size = each.value.min_size
    }

    depends_on = [aws_eks_cluster.k8s_cluster]

    ami_type = var.k8s_cluster.system_image
    instance_types = [var.k8s_cluster.instance_type]
    disk_size = each.value.disk_size

    tags = merge(
        var.k8s_cluster.module_labels,
        {
            "name" = format("%s_%s_%s_k8s_node_group", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name, each.key)
        }
    )

}

############
# Role for K8s cluster
############

resource "aws_iam_role" "k8s_role" {

    name = format("%s_%s_k8s_cluster_role", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)

    assume_role_policy = <<POLICY
{
    "Version": "2012-10-17",
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

    name = format("%s_%s_k8s_cluster_role_node_group", var.k8s_cluster.module_prefix, var.k8s_cluster.cluster_name)

    assume_role_policy = <<POLICY
{
    "Version": "2012-10-17",
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

    for_each = var.k8s_cluster.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
    role = aws_iam_role.k8s_role_node_group[each.key].name
}

resource "aws_iam_role_policy_attachment" "k8s_cni_policy" {

    for_each = var.k8s_cluster.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
    role = aws_iam_role.k8s_role_node_group[each.key].name
}

resource "aws_iam_role_policy_attachment" "k8s_container_registry_policy" {

    for_each = var.k8s_cluster.k8s_node_groups

    policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    role = aws_iam_role.k8s_role_node_group[each.key].name
}
