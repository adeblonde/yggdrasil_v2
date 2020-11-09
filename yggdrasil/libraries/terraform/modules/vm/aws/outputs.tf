output vm_parameters {
  value       = {
	vm_name = aws_instance.virtual_machine.tags.name
	private_ip = aws_instance.virtual_machine.private_ip
	subnet_full_name = data.aws_subnet.vm_subnet.tags.name
	network_full_name = data.aws_vpc.vm_vpc.tags.name
	subnet = var.vm.subnet_name
	network_name = var.vm.network_name
	user = var.vm.user
	public_ip = var.vm.subnet_type == "private" ? "0.0.0.0" : aws_instance.virtual_machine.public_ip
	ssh_key = aws_instance.virtual_machine.key_name
	group = aws_instance.virtual_machine.tags.group
  }
  description = "Map of VMs parameters"
  depends_on  = [aws_instance.virtual_machine]
}