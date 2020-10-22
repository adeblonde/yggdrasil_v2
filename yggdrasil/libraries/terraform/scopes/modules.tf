### network : contains all networks and subnets, + NAT and Internet gateways
module "network" {
  source = "../../terraform/network"

  for_each = local.formatted_network

	network = each.value
	# network_name        = each.key
	# module_labels     = each.value.module_labels
	# module_prefix       = each.value.network_module_prefix
	# private_subnets = each.value.private_subnets
	# public_subnets  = each.value.public_subnets

}

### vm : contains virtual machines + dedicated firewalls
module "vm" {
  source = "../../terraform/vm"

  for_each = local.formatted_vm

	vm = each.value
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

# ### kubernetes : contains managed kubernetes clusters
# module "kubernetes" {
#   source = "../../terraform/kubernetes"

#   for_each = var.formatted_k8s

#   k8s_cluster_name        = each.key
#   module_labels     = each.value.module_labels
#   module_prefix       = each.value.network_module_prefix
#   private_subnets = each.value.private_subnets
#   public_subnets  = each.value.public_subnets

# }