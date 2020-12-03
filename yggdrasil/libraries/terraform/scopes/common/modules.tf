### network : contains all networks and subnets, + NAT and Internet gateways
module "network" {
  source = "TERRAFORM_LIBRARY_PATH/network"

  for_each = local.formatted_network

	network = each.value
	# network_name        = each.key
	# module_labels     = each.value.module_labels
	# module_prefix       = each.value.network_module_prefix
	# private_subnets = each.value.private_subnets
	# public_subnets  = each.value.public_subnets

}

### SSH : creates and uploads SSH keys needed for reaching the VMs
module "ssh" {
	source = "TERRAFORM_LIBRARY_PATH/ssh"

	for_each = local.formatted_ssh_keys

		key = each.value
}

### IAM : Identity and Access Management (otherwise known as RBAC : Role-Based Access Control)
module "iam" {
	source = "TERRAFORM_LIBRARY_PATH/iam"

	policy = var.policy
	role = var.role
	instance_profile = var.instance_profile
	common_labels = local.common_labels["all_parts"]
	common_prefix = local.common_name_prefix["all_parts"]
}

### vm : contains virtual machines + dedicated firewalls
module "vm" {
  source = "TERRAFORM_LIBRARY_PATH/vm"

  depends_on = [module.network, module.iam]

  for_each = local.formatted_vm

	vm = each.value
	network = module.network[each.value.network_name].network_parameters
	# network_name        = each.key
	# module_labels     = each.value.module_labels
	# module_prefix       = each.value.network_module_prefix
	# instance_type = each.value.instance_type
	# availability_zone = each.value.availability_zone
	# system_image = each.value.system_image
	# subnets = each.value.subnets
	# subnet_type = each.value.subnet_type
	# private_ip = each.value.private_ip
	# root_volume = each.value.root_volume
	# data_volume = each.value.data_volume
	# ssh_public_key_path = each.value.ssh_public_key_path
	# ingress_rules = each.value.ingress_rules
	# egress_rules = each.value.egress_rules
}

### kubernetes : contains managed kubernetes clusters
module "kubernetes" {
  source = "TERRAFORM_LIBRARY_PATH/kubernetes"

  depends_on = [module.network]

  for_each = local.formatted_k8s
	
	k8s_cluster = each.value
	network = module.network[each.value.network].network_parameters
#   k8s_cluster_name        = each.key
#   module_labels     = each.value.module_labels
#   module_prefix       = each.value.network_module_prefix
#   private_subnets = each.value.private_subnets
#   public_subnets  = each.value.public_subnets

}

### container registry : create a private Docker registry
module "container_registry" {
	source = "TERRAFORM_LIBRARY_PATH/docker_registry"

	count = (var.container_registry == true ? 1 : 0)
}