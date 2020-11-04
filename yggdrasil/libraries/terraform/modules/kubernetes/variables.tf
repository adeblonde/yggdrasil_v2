variable k8s_cluster {
	type = object({
		cluster_name  = string,
		module_labels = map(string),
		module_prefix = string,
		network = string,
		subnetworks = list(string),
		zones = list(string),
		username = string,
		password = string,
		system_image = string,
		instance_type = string,
		desired_size = number
	})
}