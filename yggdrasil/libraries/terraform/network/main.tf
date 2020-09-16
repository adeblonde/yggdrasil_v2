############
# Network (VPC for AWS)
############

resource "aws_vpc" "network" {

    cidr_block = var.network_cidr
    enable_dns_hostnames = true
    enable_dns_support = true
    instance_tenancy = "default"

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_network", var.module_prefix, var.network_name)
        }
    )
}

############
# Private subnets
# isolated from Internet in ingress
############

resource "aws_subnet" "private_subnets" {

    for_each = var.private_subnets

    vpc_id = aws_vpc.network.vpc_id
    cidr_block = each.value.cidr_block
    availability_zone = each.value.availability_zone
    map_public_ip_on_launch = false

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_%s_private_subnet", var.module_prefix, var.network_name, each.value.private_subnet_name)
        }
    )
}

############
# Internet Gateway
# allows private subnets to reach Internet in egress
############

resource "aws_internet_gateway" "internet_gateway" {

    vpc_id = aws_vpc.network.vpc_id

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_internet_gateway", var.module_prefix, var.network_name)
        }
    )

}

############
# Private route tables
############

resource "aws_route_table" "public_route_tables" {
    
}

############
# Public subnets
# accessible from Internet in ingress
############

resource "aws_subnet" "public_subnets" {

    for_each = var.public_subnets

    vpc_id = aws_vpc.network.vpc_id
    cidr_block = each.value.cidr_block
    availability_zone = each.value.availability_zone
    map_public_ip_on_launch = false

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_%s_private_subnet", var.module_prefix, var.network_name, each.value.public_subnet_name)
        }
    )
}

############
# NAT Gateway
# allows public subnets to reach other subnets
############

resource "aws_internet_gateway" "nat_gateway" {

    for_each = var.public_subnets

    vpc_id = aws_vpc.network.vpc_id

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_%s_nat_gateway", var.module_prefix, var.network_name,, each.value.public_subnet_name)
        }
    )

}

