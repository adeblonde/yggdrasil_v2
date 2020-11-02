output requested_networks {
  value       = local.formatted_network
  description = "Map of requested networks"
}

output requested_vms {
  value       = local.formatted_vm
  description = "Map of requested vms"
}

output common_labels {
	value = local.common_labels
}

output common_name_prefix {
  value       = local.common_name_prefix
  description = "description"
  depends_on  = []
}

output vms {
  value       = {
	  for vm_name, vm in module.vm :
	  	vm_name => vm.vm_parameters
  }
  description = "description"
  depends_on  = []
}

output networks {
  value       = {
	  for network_name, network in module.network :
	  	network_name => network.network_parameters
  }
  description = "description"
  depends_on  = []
}