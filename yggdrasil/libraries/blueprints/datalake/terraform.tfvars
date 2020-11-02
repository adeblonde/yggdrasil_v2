### select cloud provider
cloud_provider = "gcp"

### labels
account = "acc"
cost_center = "cc"
parts = {
	part = ["subpart_1", "subpart_2"]
}
environment = "dev"

# account = "dflt_acc"
# cost_center = "cost_ctr"
# parts = {
# 	part = ["subpart_1", "subpart_2"]
# }
# environment = "dev"

### owner
owner = "devops"

### region
region = "us-west1"

### types
types = {
	gcp = {
		bastion = "e2-micro"
		backend = "e2-small"
	}
}

### SSH keys
ssh_public_key_folder = "../../secrets/ssh/SCOPE/public/"

### OS user
os_user = "debian"