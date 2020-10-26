# ############
# # Security Group / Firewall group
# ############

resource "google_compute_firewall" "security_group_vm" {
	
	name = substr(replace(format("%s_%s_sg", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
	network = var.vm.network_name
	direction = "INGRESS"

	allow {
		protocol = "icmp"
	}

	allow {
		protocol = "tcp"
		ports = [for rule in var.vm.ingress_rules : rule.to_port]
	}
}

############
# Virtual Machine
############
# data "google_compute_image" "vm_image" {
# #   family  = var.vm.system_image
#   name = var.vm.system_image
# }

resource "google_compute_instance" "virtual_machine" {

	depends_on = [google_compute_firewall.security_group_vm]
	
	name = substr(replace(format("%s_%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
	machine_type = var.vm.instance_type
	zone = var.vm.availability_zone

	boot_disk {
		initialize_params {
			image = var.vm.system_image
			# image = data.google_compute_image.vm_image.name
			size = var.vm.root_volume.size
			type = var.vm.root_volume.type
		}
	}

	network_interface {
		network = substr(replace(format("%s_%s_network", var.vm.module_prefix, var.vm.network_name), "_", "-"), 0, 61)
		subnetwork = substr(replace(format("%s_%s_%s_%s_subnet", var.vm.module_prefix, var.vm.network_name, var.vm.subnet_name, var.vm.subnet_type), "_", "-"), 0, 61)
		network_ip = var.vm.private_ip
	}

	### dynamic creation of public IPs
	dynamic "network_interface" {
		for_each = google_compute_address.elastic_ip

		content {
			subnetwork = substr(replace(format("%s_%s_%s_%s_subnet", var.vm.module_prefix, var.vm.network_name, var.vm.subnet_name, var.vm.subnet_type), "_", "-"), 0, 61)
			access_config {
				nat_ip = network_interface.value.address
			}
		}
	}

	# root_block_device {
	# 	type = var.vm.root_volume.type
	# 	size = var.vm.root_volume.size
	# 	auto_delete = true
	# }

	lifecycle {
		ignore_changes = [attached_disk]
	}

	service_account {
		scopes = []
	}

	labels = merge(
        var.vm.module_labels,
        {
            "name" = substr(replace(format("%s_%s_vm_root_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
			"group" = var.vm.group,
			"ssh_key" = format("%s_key", var.vm.module_prefix)
        } 
    )

	metadata = {
    	ssh-keys = "${var.vm.user}:${file(format("%s%s_public.pem", var.vm.ssh_public_key_path, var.vm.module_prefix))}"
  	}

}

############
# Data Volume
############

resource "google_compute_disk" "vm_data_volume" {

	count = (var.vm.data_volume.size > 0 ? 1 : 0)

	name = substr(replace(format("%s_%s_data_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)

	physical_block_size_bytes = var.vm.data_volume.size
	type = var.vm.data_volume.type

	labels = merge(
        var.vm.module_labels,
        {
            "name" = substr(replace(format("%s_%s_data_volume", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)
        }
    )

	zone = var.vm.availability_zone

}

resource "google_compute_attached_disk" "default" {

	count = (var.vm.data_volume.size > 0 ? 1 : 0)

	disk     = google_compute_disk.vm_data_volume.0.id
	instance = google_compute_instance.virtual_machine.id
}

############
# Static public IP
############

resource "google_compute_address" "elastic_ip" {

	count = (var.vm.subnet_type == "public" ? 1 : 0)

	name = substr(replace(format("%s_%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name), "_", "-"), 0, 61)

	# labels = merge(
    #     var.vm.module_labels,
    #     {
    #         "name" = substr(replace(format("%s_%s_elastic_ip", var.vm.module_prefix, var.vm.vm_name)
    #     }
    # )

}