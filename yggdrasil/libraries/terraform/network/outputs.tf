output "network_id" {
    description = "Network ID"
    value = aws_vpc.vpc.id
}

output "public_subnets_ids" {
    description = "Public subnets IDs"
    value = {
        for public_subnet in aws_subnet.public_subnets :
            public_subnet.tags["name"] => public_subnet.id
    }
}

output "private_subnets_ids" {
    description = "Private subnets IDs"
    value = {
        for private_subnet in aws_subnet.private_subnets :
            private_subnet.tags["name"] => private_subnet.id
    }
}