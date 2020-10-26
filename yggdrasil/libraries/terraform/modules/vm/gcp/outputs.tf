output vm_parameters {
  value       = {
	private_ip = google_compute_instance.virtual_machine.network_interface.0.network_ip
	subnet = google_compute_instance.virtual_machine.network_interface.0.subnetwork
	network = google_compute_instance.virtual_machine.network_interface.0.network
	public_ip = google_compute_instance.virtual_machine.network_interface.*.network_ip
	ssh_key = google_compute_instance.virtual_machine.labels.ssh_key
	group = google_compute_instance.virtual_machine.labels.group
  }
  description = "Map of VMs private ips"
  depends_on  = [google_compute_instance.virtual_machine]
}