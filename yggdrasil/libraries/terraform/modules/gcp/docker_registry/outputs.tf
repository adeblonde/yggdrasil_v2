output docker_registry {
  value       = google_container_registry.registry.bucket_self_link
  sensitive   = true
  description = "description"
  depends_on  = []
}
