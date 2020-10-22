variable vm {
	description = "Map of parameters for virtual machine"
	type = object({
		vm = string
		network_name = string
		module_labels = string
		module_prefix = string
		instance_type = string
		availability_zone = string
		system_image = string
		subnets = string
		subnet_type = string
		private_ip = string
		root_volume = string
		data_volume = string
		ssh_public_key_path = string
		ingress_rules = string
		egress_rules = string
	})
}