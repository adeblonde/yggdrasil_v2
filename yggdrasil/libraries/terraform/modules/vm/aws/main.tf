############
# Security Group / Firewall group
############

resource "aws_security_group" "security_group_vm" {
	
	name = format("%s_%s_sg", var.module_prefix, var.vm_name)
	description = var.description
	vpc_id = var.network_ids[var.network_name]
	revoke_rules_on_delete = true

	dynamic "ingress" {
		for_each = var.ingress_rules

		content {
			description = ingress.value.description
			from_port = ingress.value.from_port
			to_port = ingress.value.to_port
			protocol = ingress.value.protocol
			cidr = ingress.value.cidr
		}
	}

	dynamic "egress" {
		for_each = var.egress_rules

		content {
			description = egress.value.description
			from_port = egress.value.from_port
			to_port = egress.value.to_port
			protocol = egress.value.protocol
			cidr = egress.value.cidr
		}
	}

	tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_firewall", var.module_prefix, var.vm_name)
        }
    )
}

############
# Virtual Machine
############

resource "aws_instance" "virtual_machine" {

	depends_on = [aws_security_group.security_group_vm]
	ami = var.system_image
	aws_instance = var.instance_type
	vpc_security_group_ids = [aws_security_group.security_group_vm.network_id]

	availability_zone = var.availability_zone
	key_name = var.key_name
	subnet_id = var.subnet_ids[format("%s_%s_%s_%s_subnet", var.network_module_prefix, var.network_name, var.subnet_name, var.subnet_type)]
	associate_public_ip_address = (var.subnet_type == "public" ? true : false)
	private_ip = var.private_ip
	source_dest_check = true

	root_block_device {
		volume_type = var.root_volume.type
		volume_size = var.root_volume.size
		delete_on_termination = true
	}

	iam_instance_profile = format("%s_%s_instance_profile", var.iam_module_prefix, var.instance_profile_name)

		tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_virtual_machine", var.module_prefix, var.vm_name)
        }
    )

	volume_tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_vm_root_volume", var.module_prefix, var.vm_name)
        }
    )

}

############
# Data Volume
############

resource "aws_ebs_volume" "vm_data_volume" {

	count = (var.data_volume.size > 0 ? 1 : 0)

	size = var.data_volume.size
	type = var.data_volume.type

	tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_data_volume", var.module_prefix, var.vm_name)
        }
    )

	availability_zone = var.availability_zone

}

resource "aws_volume_attachment" "vm_data_volume_attachment" {

	count = (var.data_volume.size > 0 ? 1 : 0)
	
	device_name = var.data_volume_name
	volume_id = aws_ebs_volume.vm_data_volume.id
	instance_id = aws_instance.virtual_machine.id

}

############
# Static public IP
############

resource "aws_eip" "elastic_ip" {

	count = (var.subnet_type == "public" ? 1 : 0)

	depends_on = [aws_instance.virtual_machine]
	instance = aws_instance.virtual_machine.id

	tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_elastic_ip", var.module_prefix, var.vm_name)
        }
    )

}