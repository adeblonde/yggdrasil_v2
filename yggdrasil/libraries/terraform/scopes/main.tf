### reformatting of input variables
locals {

	### map of all common labels for all resources
	common_labels_seed = {
		provider = var.cloud_provider
		account = var.account
		cost_center = var.cost_center
		part = var.part
		subpart = var.subpart
		environment = var.environment
	}

	### map of labels per part and subpart
	common_labels = merge(
		{ for part in var.part :
		part => merge(
			{ for subpart in var.subpart :
			subpart => merge(
				{
					part  = part
					subpart = subpart
				},
				local.common_labels_seed)
			},
			{ "all_subparts" = merge(
				{ 
					part = part }
				,
				local.common_labels_seed
				)
			}
		)
		},
		{ "all_parts" = local.common_labels_seed }
	)

	### building common name prefixes
	common_name_prefix = merge(
		{ for part in var.part :
		part => merge(
			{ for subpart in var.subpart :
			subpart => format("%s_%s_%s_%s_%s", var.account, var.cost_center, var.environment, part, subpart)
			},
			{ "all_subparts" = format("%s_%s_%s_%s", var.account, var.cost_center, var.environment, part)
			}
		)
		},
		{ "all_parts" = format("%s_%s_%s", var.account, var.cost_center, var.environment) }
	)

	### formatting networks
	formatted_network = { for network_key, network in var.network :
		network_key => {
			network_name        = network_key
			module_labels     = local.common_labels[network.part]["all_subparts"]
			module_prefix       = local.common_name_prefix[network.part]["all_subparts"]
			private_subnets = network.private_subnets
			public_subnets  = network.public_subnets
		}
	}

	### formatting private subnets
	formatted_private_subnets = flatten([])

	### formatting virtual machines
	formatted_vm_list = flatten([
		for part_key, part in var.vm : [
			for subpart_key, subpart in part : [
				for vm_name, vm in subpart : {
					name = vm_name
					network_name = vm.network
					subnet_name = vm.subnet_name
					module_labels     = local.common_labels[part_key][subpart_key]
					module_prefix       = local.common_name_prefix[part_key][subpart_key]
					instance_type = lookup(var.types[var.cloud_provider], vm.type)
					availability_zone = vm.availability_zone
					system_image = lookup(var.system_images, vm.system_image)
					subnet_type = vm.subnet_type
					private_ip = vm.private_ip
					root_volume = var.generic_volume_parameters[vm.root_volume_type]
					data_volume = var.generic_volume_parameters[vm.data_volume_type]
					data_disk_id         = lookup(vm, "data_disk_id", "/dev/sdf")
					ssh_public_key_path = format("%s%s.pub", var.ssh_public_key_folder, vm.ssh_key)
					ingress_rules = { for rule in vm.ingress_rules :
						rule => {
							description = var.ingress_rules[rule].description
							from_port   = var.ingress_rules[rule].from_port
							to_port     = var.ingress_rules[rule].to_port
							protocol    = var.ingress_rules[rule].protocol
							cidr        = lookup(vm.ingress_cidr, rule, ["0.0.0.0/0"])
						}
					}
					egress_rules = { for rule in vm.egress_rules :
						rule => {
							description = var.egress_rules[rule].description
							from_port   = var.egress_rules[rule].from_port
							to_port     = var.egress_rules[rule].to_port
							protocol    = var.egress_rules[rule].protocol
							cidr        = lookup(vm.egress_cidr, rule, ["0.0.0.0/0"])
						}
					}
				}
			]
		]
	])

	formatted_vm = { for vm in local.formatted_vm_list :
		vm.name => vm
	}

}