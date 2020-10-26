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
  sensitive   = true
  description = "description"
  depends_on  = []
}

# output vm_request_vms {
# 	value = module.vm["first_public_vm"]
# }