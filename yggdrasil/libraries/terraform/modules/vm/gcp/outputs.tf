output vm_parameters {
  value       = {
	  for vm in google_compute_instance.virtual_machine :
	  vm.name => {
		private_ip = vm.network_interface.0.network_ip
		subnet = vm.network_interface.0.subnetwork
		network = vm.network_interface.0.network
		public_ip = vm.network_interface[length(vm.network_interface)].network_ip
		ssh_key = vm.labels.ssh_key
		group = vm.labels.group
	  }
  }
  description = "Map of VMs private ips"
  depends_on  = [google_compute_instance.virtual_machine]
}