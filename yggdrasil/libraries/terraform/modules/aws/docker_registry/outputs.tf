output docker_registry {
  value       = aws_ecr_repository.registry.repository_url
  sensitive   = true
  description = "description"
  depends_on  = []
}
