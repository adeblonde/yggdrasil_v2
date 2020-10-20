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
resource "google_compute_instance" "virtual_machine" {

	depends_on = [aws_security_group.security_group_vm]
	
	name = format("%s_%s_vm_root_volume", var.module_prefix, var.vm_name)
	machine_type = var.instance_type
	zone = var.availability_zone

	boot_disk {
		initialize_params {
			image = var.system_image
		}
	}

	network_interface {
		subnetwork = var.subnets[format("%s_%s_%s_%s_subnet", var.network_module_prefix, var.network_name, var.subnet_name, var.subnet_type)]
		network_ip = var.private_ip
	}

	### dynamic creation of public IPs
	dynamic "network_interface" {
		for_each = google_compute_address.elastic_ip

		content {
			network_interface = {
				subnetwork = var.subnets[format("%s_%s_%s_%s_subnet", var.network_module_prefix, var.network_name, var.subnet_name, var.subnet_type)]
				access_config = {
					nat_ip = network_interface.value.associate_public_ip_address
				}
			}
		}
	}

	root_block_device {
		type = var.root_volume.type
		size = var.root_volume.size
		auto_delete = true
	}

	lifecycle {
		ignore_changes = [attached_disk]
	}

	service_account {
		scopes = []
	}

	labels = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_vm_root_volume", var.module_prefix, var.vm_name)
        }
    )

	metadata = {
    	ssh-keys = "${var.user}:${file(var.ssh_public_key_path)}"
  	}

}

############
# Data Volume
############

resource "google_compute_disk" "vm_data_volume" {

	count = (var.data_volume.size > 0 ? 1 : 0)

	name = format("%s_%s_data_volume", var.module_prefix, var.vm_name)

	physical_block_size_bytes = var.data_volume.size
	type = var.data_volume.type

	labels = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_data_volume", var.module_prefix, var.vm_name)
        }
    )

	zone = var.availability_zone

}

resource "google_compute_attached_disk" "default" {

	count = (var.data_volume.size > 0 ? 1 : 0)

	disk     = google_compute_disk.vm_data_volume.id
	instance = google_compute_instance.virtual_machine.id
}

############
# Static public IP
############

resource "google_compute_address" "elastic_ip" {

	count = (var.subnet_type == "public" ? 1 : 0)

	depends_on = [aws_instance.virtual_machine]
	name = format("%s_%s_elastic_ip", var.module_prefix, var.vm_name)

	labels = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_elastic_ip", var.module_prefix, var.vm_name)
        }
    )

}