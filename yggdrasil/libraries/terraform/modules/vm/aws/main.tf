############
# Security Group / Firewall group
############

data "aws_vpc" "vm_vpc" {
	filter {
		name = "tag:name"
		values = [format("%s_%s_network", var.vm.network_prefix, var.vm.network_name)]
	}
}

resource "aws_security_group" "security_group_vm" {
	
	name = format("%s_%s_sg", var.vm.module_prefix, var.vm.vm_name)
	description = "Description VM"
	# description = var.vm.description
	vpc_id = data.aws_vpc.vm_vpc.id
	revoke_rules_on_delete = true

	dynamic "ingress" {
		for_each = var.vm.ingress_rules

		content {
			description = ingress.value.description
			from_port = ingress.value.from_port
			to_port = ingress.value.to_port
			protocol = ingress.value.protocol
			cidr_blocks = ingress.value.cidr
		}
	}

	dynamic "egress" {
		for_each = var.vm.egress_rules

		content {
			description = egress.value.description
			from_port = egress.value.from_port
			to_port = egress.value.to_port
			protocol = egress.value.protocol
			cidr_blocks = egress.value.cidr
		}
	}

	tags = merge(
        var.vm.module_labels,
        {
            "name" = format("%s_%s_firewall", var.vm.module_prefix, var.vm.vm_name)
        }
    )
}

############
# Virtual Machine
############

data "aws_subnet" "vm_subnet" {
	filter {
		name = "tag:name"
		values = [format("%s_%s_%s_%s_subnet", var.vm.network_prefix, var.vm.network_name, var.vm.subnet_name, var.vm.subnet_type)]
	}
}

resource "aws_instance" "virtual_machine" {

	depends_on = [aws_security_group.security_group_vm]
	ami = var.vm.system_image
	instance_type = var.vm.instance_type
	vpc_security_group_ids = [aws_security_group.security_group_vm.id]

	availability_zone = var.vm.availability_zone
	key_name = var.vm.key_name
	subnet_id = data.aws_subnet.vm_subnet.id
	associate_public_ip_address = (var.vm.subnet_type == "public" ? true : false)
	private_ip = var.vm.private_ip
	source_dest_check = true

	root_block_device {
		volume_type = var.vm.root_volume.type
		volume_size = var.vm.root_volume.size
		delete_on_termination = true
	}

	iam_instance_profile = format("%s_%s_instance_profile", var.vm.iam_module_prefix, var.vm.instance_profile_name)

		tags = merge(
        var.vm.module_labels,
        {
            "name" = format("%s_%s_virtual_machine", var.vm.module_prefix, var.vm.vm_name)
        }
    )

	volume_tags = merge(
        var.vm.module_labels,
        {
            "name" = format("%s_%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name)
        }
    )

}

############
# Data Volume
############

resource "aws_ebs_volume" "vm_data_volume" {

	count = (var.vm.data_volume.size > 0 ? 1 : 0)

	size = var.vm.data_volume.size
	type = var.vm.data_volume.type

	tags = merge(
        var.vm.module_labels,
        {
            "name" = format("%s_%s_data_volume", var.vm.module_prefix, var.vm.vm_name)
        }
    )

	availability_zone = var.vm.availability_zone

}

resource "aws_volume_attachment" "vm_data_volume_attachment" {

	count = (var.vm.data_volume.size > 0 ? 1 : 0)
	
	device_name = var.vm.data_volume_name
	volume_id = aws_ebs_volume.vm_data_volume.0.id
	instance_id = aws_instance.virtual_machine.id

}

############
# Static public IP
############

resource "aws_eip" "elastic_ip" {

	count = (var.vm.subnet_type == "public" ? 1 : 0)

	depends_on = [aws_instance.virtual_machine]
	instance = aws_instance.virtual_machine.id

	tags = merge(
        var.vm.module_labels,
        {
            "name" = format("%s_%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name)
        }
    )

}