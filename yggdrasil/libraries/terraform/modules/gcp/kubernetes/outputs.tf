output kubernetes_parameters {
  value       = {
	  kubernetes_cluster_endpoint = google_container_cluster.k8s_cluster.endpoint
	  kubernetes_cluster_id = google_container_cluster.k8s_cluster.id
	  kubernetes_cluster_certificate_authority = google_container_cluster.k8s_cluster.master_auth.0.cluster_ca_certificate 
	  kubernetes_cluster_full_name = google_container_cluster.k8s_cluster.name
	#   kubernetes_cluster_certificate = google_container_cluster.k8s_cluster.master_auth.0.client_certificate 
	#   kubernetes_cluster_client_key = google_container_cluster.k8s_cluster.master_auth.0.client_key 
	#   kubernetes_cluster_cluster_ca_certificate = google_container_cluster.k8s_cluster.master_auth.0.cluster_ca_certificate
  }
  sensitive   = true
  description = "Map of kubernetes clusters parameters"
  depends_on  = []
}
