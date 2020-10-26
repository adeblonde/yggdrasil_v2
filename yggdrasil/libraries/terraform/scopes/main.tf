### reformatting of input variables
locals {

	### map of all common labels for all resources
	common_labels_seed = {
		provider = var.cloud_provider
		account = var.account
		cost_center = var.cost_center
		environment = var.environment
	}

	### map of labels per part and subpart
	common_labels = merge(
		{ for part, subparts in var.parts :
		part => merge(
			{ for subpart in subparts :
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
		{ for part, subparts in var.parts :
		part => merge(
			{ for subpart in subparts :
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
			network_cidr = network.network_cidr
			module_labels     = local.common_labels[network.part]["all_subparts"]
			module_prefix       = local.common_name_prefix[network.part]["all_subparts"]
			private_subnets = network.private_subnets
			public_subnets  = network.public_subnets
		}
	}

	### formatting private subnets
	# formatted_private_subnets = flatten([])

	### formatting virtual machines
	formatted_vm_list = flatten([
		for network_name, network_vms in var.vm : [
			for subnet_name, subnet_vms in network_vms : [
				for vm_name, vm in subnet_vms : {
					vm_name = vm_name
					user = vm.user
					network_name = network_name
					subnet_name = subnet_name
					module_labels     = local.common_labels[vm.part][vm.subpart]
					module_prefix       = local.common_name_prefix[vm.part][vm.subpart]
					group = vm.group
					instance_type = lookup(var.types[var.cloud_provider], vm.type)
					availability_zone = vm.availability_zone
					system_image = lookup(var.system_images, vm.system_image)
					subnet_type = vm.subnet_type
					private_ip = vm.private_ip
					root_volume = var.generic_volume_parameters[vm.root_volume_type]
					data_volume = var.generic_volume_parameters[lookup(vm, "data_volume_type", "none")]
					data_disk_id         = lookup(vm, "data_disk_id", "/dev/sdf")
					# ssh_public_key_path = format("%s%s.pub", var.ssh_public_key_folder, var.vm.ssh_key)
					ssh_public_key_path = var.ssh_public_key_folder
					ingress_rules = { for rule in vm.ingress_rules :
						rule => {
							description = var.ingress_rules[rule].description
							from_port   = var.ingress_rules[rule].from_port
							to_port     = var.ingress_rules[rule].to_port
							protocol    = var.ingress_rules[rule].protocol
							cidr        = lookup(lookup(vm, "ingress_cidr", {}), rule, ["0.0.0.0/0"])
						}
					}
					egress_rules = { for rule in vm.egress_rules :
						rule => {
							description = var.egress_rules[rule].description
							from_port   = var.egress_rules[rule].from_port
							to_port     = var.egress_rules[rule].to_port
							protocol    = var.egress_rules[rule].protocol
							cidr        = lookup(lookup(vm, "egress_cidr", {}), rule, ["0.0.0.0/0"])
						}
					}
				}
			]
		]
	])

	formatted_vm = { for vm in local.formatted_vm_list :
		vm.vm_name => vm
	}

}