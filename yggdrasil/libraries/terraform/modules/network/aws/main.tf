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
# Internet Gateway
# allows communication between network and Internet, both ways
# all VMs with a public IP are allowed to reach the Internet
# through the Internet Gateway
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
# elastic IP for the NAT Gateway
############

resource "aws_eip" "elastic_ip" {

    vpc = true
    depends_on = [aws_internet_gateway.internet_gateway]

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_elastic_ip", var.module_prefix, var.network_name)
        }
    )
}

############
# NAT Gateway
# allows communication from subnets to Internet egress only (for private subnets)
# used with an elastic IP
# The NAT Gateway allows all private VMs (i.e. without a public IP) to reach Internet, with the same IP (the one from the NAT Gateway)
############

resource "aws_nat_gateway" "nat_gateway" {

    for_each = var.public_subnets

    allocation_id = aws_eip.elastic_ip.id
    subnet_id = aws_subnet.public_subnets[each.key].id

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_%s_nat_gateway", var.module_prefix, var.network_name, each.value.public_subnet_name)
        }
    )

}

############
# Private route tables
# allow resources to reach other resources on networks
############

resource "aws_route_table" "private_route_tables" {

    for_each = var.private_subnets

    vpc_id = aws_vpc.network.vpc_id
    route {
        cidr_block = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.nat_gateway[each.value.attached_public_subnet].id
    }
}

resource "aws_route_table_association" "private_rta" {

    for_each = var.private_subnets

    subnet_id = aws_subnet.private_subnets[each.value].id
    route_table_id = aws_route_table.private_subnets[each.value].id
}

############
# Public route tables
# allow resources to reach other resources on networks
############

resource "aws_route_table" "public_route_tables" {

    for_each = var.public_subnets

    vpc_id = aws_vpc.network.vpc_id
    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.internet_gateway.id
    }
}

resource "aws_route_table_association" "public_rta" {

    for_each = var.public_subnets

    subnet_id = aws_subnet.public_subnets[each.value].id
    route_table_id = aws_route_table.public_subnets[each.value].id
}