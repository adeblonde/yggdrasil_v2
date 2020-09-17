variable "k8s_cluster_name" {
    type = string
    description = "Name of the virtual machine"
}

variable "description" {
    type = string
    description = "Description of the virtual machine"
}

variable "network_name" {
    type = string
    description = "Name of the network"
}

variable "network_ids" {
    description = "List of networks' ids"
}

variable "ingress_rules" {
    description = "List of ingress rules"
}

variable "egress_rules" {
    description = "List of egress rules"
}

variable "system_image" {
    description = "Name of virtual machine OS image"
}

variable "instance_type" {
    description = "Type of instance"
}

variable "subnet_ids" {
    description = "List of subnet ids"
}

variable "k8s_cluster_subnets" {
    description = "List of subnet names for the virtual machine"
}

variable "k8s_node_groups" {
    description = "List of structured node groups with their parameters"
}

variable "disk_size" {
    description = "Disk size for worker nodes"
}

variable "module_tags" {
    description = "List of all the tags of the module"
}

variable "module_prefix" {
    description = "Prefix used for resource' names in the module"
}