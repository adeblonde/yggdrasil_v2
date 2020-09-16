############
# Security Group / Firewall group
############

resource "aws_security_group" "security_group_vm" {
	
	name = format("%s_%s_sg", var.module_prefix, var.vm_name)
	description = var.description
	vpc_id = var.network_ids[var.network_name]
	revoke_rules_on_delete = true

	tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_network", var.module_prefix, var.vm_name)
        }
    )

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
}

############
# Virtual Machine
############

resource 