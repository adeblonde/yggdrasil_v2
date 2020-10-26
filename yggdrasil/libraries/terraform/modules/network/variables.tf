# variable network {
#   type        = map(object({
# 	network_name  = string,
# 	module_labels = map(string),
# 	module_prefix = string,
# 	private_subnets = object({
# 		subnet_name = string,
# 		cidr_block = string,
# 		subnet_type = string
# 	}),
# 	public_subnets = object({
# 		subnet_name = string,
# 		cidr_block = string,
# 		subnet_type = string
# 	})
#   }))
# #   default     = ""
#   description = "Map of parameters for network and associated subnets"
# }

variable network {

}
