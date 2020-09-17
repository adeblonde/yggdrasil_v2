output "cluster_id" {
    value = aws_eks_cluster.k8s_cluster.arn
}

output "cluster_endpoint" {
    value = aws_eks_cluster.k8s_cluster.endpoint
}

output "cluster_certificate_authority" {
    value = aws_eks_cluster.k8s_cluster.certificate_authority
}

output "cluster_name" {
    value = aws_eks_cluster.k8s_cluster.id
}