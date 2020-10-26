# variable vm {
# 	description = "Map of parameters for virtual machine"
# 	type = map(object({
# 		vm_name = string,
# 		user = string,
# 		network_name = string,
# 		module_labels = map(string),
# 		module_prefix = string,
# 		group = string,
# 		instance_type = string,
# 		availability_zone = string,
# 		system_image = string,
# 		subnet_name = string,
# 		subnet_type = string,
# 		private_ip = string,
# 		root_volume = map(string),
# 		data_volume = map(string),
# 		ssh_public_key_path = string,
# 		ingress_rules = map(any),
# 		egress_rules = map(any)
# 	}))
# }

variable vm {
}