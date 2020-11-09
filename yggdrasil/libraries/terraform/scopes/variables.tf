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

variable "parts" {
	description = "Way for annotating resources : parts"
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
	description = "Map of all networks and subnets"
	type = map(object({
		network_cidr = string
		part = string
		public_subnets = map(
			object({
				cidr_block = string
				availability_zone = string
			})
		)
		private_subnets = map(
			object({
				cidr_block = string
				availability_zone = string
			})
		)
		private_subnets_escape_public_subnet = string
	}))
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
  description = "path to public SSH keys in target workfolder"
}

### OS user
variable os_user {
	description = "name of the user for VMs"
	type = string
}

### kubernetes clusters
variable k8s_cluster {
	description = "Map of all managed kubernetes clusters"
	type = map(any)
}

### container registry
variable container_registry {
	description = "A Docker registry for the whole project"
	type = bool
}