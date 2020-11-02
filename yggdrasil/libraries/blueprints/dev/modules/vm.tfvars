### description of all virtual machines in HCL format
vm = {
	main_network = {
		fst_pb_subnet = {
			fst_pb_vm = {
				user = "debian"
				group = "bastion"
				type = "bastion"
				part = "part"
				subpart = "subpart_1"
				availability_zone = "us-west1-a"
				system_image = "debian"
				subnet_type = "public"
				private_ip = "10.0.1.3"
				root_volume_type = "small_root"
				ingress_rules = ["ssh"]
				ingress_cidr = {
					"ssh" = "0.0.0.0/0"
				}
				egress_rules = ["default"]
			}
		}
		fst_pv_subnet = {
			fst_pv_vm = {
				user = "debian"
				group = "backend"
				type = "backend"
				part = "part"
				subpart = "subpart_2"
				availability_zone = "us-west1-a"
				system_image = "debian"
				subnet_type = "private"
				private_ip = "10.0.3.3"
				root_volume_type = "small_root"
				data_volume_type = "large_data"
				ingress_rules = ["ssh", "https", "http"]
				egress_rules = ["default"]
			}
		}
	}
}