variable network {
  type        = object({
	network_name  = string
	module_labels = string
	module_prefix = string
	private_subnets = string
	public_subnets = string
  })
#   default     = ""
  description = "Map of parameters for network and associated subnets"
}
