variable "network_name" {
    type = string
    description = "Name of the network"
}

variable "private_subnets" {
   description = "List of the private subnets' names"
}

variable "public_subnets" {
   description = "List of the public subnets' names"
}

variable "module_tags" {
    description = "List of all the tags of the module"
}

variable "module_prefix" {
    description = "Prefix used for resource' names in the module"
}