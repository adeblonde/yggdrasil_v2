### main variables
variable "cloud_provider" {
	description = "Cloud provider name"
}

variable "account" {
	description = "Cloud project account"
}

variable "cost_center" {
	description = "Cost center for the project"
}

variable "part" {
	description = "Way for annotating resources : parts"
}

variable "subpart" {
	description = "Way for annotating resources : subparts"
}

variable "environment" {
	description = "Environment tag for resources : dev, preprod, prod, etc"
}

variable "owner" {
	description = "Role owner name for managing cloud resources"
}

variable "region" {
	description = "Cloud region/datacenter name"
}

### provider-specific parameters
variable system_images {
  type        = map
  description = "description"
}

variable generic_volume_parameters {
  description = "description"
}

variable ingress_rules {
  description = "description"
}

variable egress_rules {
  description = "description"
}

### network variables
variable "network" {

}

### vm variables
variable vm {
  description = "description"
}

variable types {
  description = "description"
}

### SSH keys
variable ssh_public_key_folder {
  description = "description"
}

