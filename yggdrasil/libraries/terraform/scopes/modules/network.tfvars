### description of all networks and subnetworks in HCL format
network = {
	main_network = {
		network_cidr = "10.0.0.0/16"
		part = "part"
		public_subnets = {
			fst_pb_subnet = {
				cidr_block = "10.0.1.0/24"
			}
			snd_pb_subnet = {
				cidr_block = "10.0.2.0/24"
			}
		}
		private_subnets = {
			fst_pv_subnet = {
			cidr_block = "10.0.3.0/24"
				private_subnets_escape_public_subnet = "first_public_subnet"
			}
			snd_pv_subnet = {
				cidr_block = "10.0.4.0/24"
				private_subnets_escape_public_subnet = "second_public_subnet"
			}
		}
	}
}