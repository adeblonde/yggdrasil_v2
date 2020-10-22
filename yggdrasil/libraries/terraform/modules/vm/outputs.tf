output "public_ip" {
    description = "Public IP of virtual machine"
    value = {
        aws_instance.virtual_machine.tags["name"] => aws_instance.virtual_machine.public_ip
    }
}

output "private_ips" {
    description = "Private IP of virtual machine"
    value = {
        aws_instance.virtual_machine.tags["name"] => aws_instance.virtual_machine.private_ip
    }
}