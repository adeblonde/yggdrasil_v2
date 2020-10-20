provider "google" {
	credentials = file("CREDENTIALS_FILE")
	project = "PROJECT_ID"
	region = "REGION"
}