### system images
system_images = {
	gcp = {
		debian = "debian-9"
		ubuntu_server = "ubuntu-2004-lts"
		centos = "centos-8"
	}	
}

### GCP disk types :
# pd-standard : HDD
# pd-ssd : SSD
# pd-balanced : cheaper SSD
generic_volume_parameters = {
	small_root = {
		type = "pd-ssd"
		size = 16
	}
	large_root = {
		type = "pd-ssd"
		size = 32
	}
	large_data = {
		type = "pd-standard"
		size = 128
	}
	none = {
		type = "pd-standard"
		size = 0
	}
}

### firewall rules
ingress_rules = {
	"ssh" = {
		from_port   = 22
		to_port     = 22
		protocol    = "tcp"
		description = "SSH connection"
		cidr = ["0.0.0.0/0"]
	},
	"icmp" = {
		from_port   = -1
		to_port     = -1
		protocol    = "icmp"
		description = "Ping response"
		cidr = ["0.0.0.0/0"]
	},
	"kafka-ui" = {
		from_port   = 9021
		to_port     = 9021
		protocol    = "tcp"
		description = "Kafka UI web"
		cidr = ["0.0.0.0/0"]
	},
	"kafka-rest" = {
		from_port   = 8082
		to_port     = 8082
		protocol    = "tcp"
		description = "Kafka REST API"
		cidr = ["0.0.0.0/0"]
	},
	"kafka" = {
		from_port   = 9092
		to_port     = 9092
		protocol    = "tcp"
		description = "Kafka Connect API"
		cidr = ["0.0.0.0/0"]
	},
	"zookeeper-ui" = {
		from_port   = 9021
		to_port     = 9021
		protocol    = "tcp"
		description = "Kafka UI web"
		cidr = ["0.0.0.0/0"]
	},
	"zookeeper" = {
		from_port   = 2181
		to_port     = 2181
		protocol    = "tcp"
		description = "Kafka UI web"
		cidr = ["0.0.0.0/0"]
	},
	"ftp_listen" = {
		from_port   = 21
		to_port     = 21
		protocol    = "tcp"
		description = "FTP listening"
		cidr = ["0.0.0.0/0"]
	},
	"ftps" = {
		from_port   = 990
		to_port     = 990
		protocol    = "tcp"
		description = "FTPS"
		cidr = ["0.0.0.0/0"]
	},
	"ftp_data" = {
		from_port   = 20
		to_port     = 20
		protocol    = "tcp"
		description = "FTP data"
		cidr = ["0.0.0.0/0"]
	},
	"ftp_passive" = {
		from_port   = 10000
		to_port     = 11000
		protocol    = "tcp"
		description = "FTP passive"
		cidr = ["0.0.0.0/0"]
	},
	"kafka_schema_registry" = {
		from_port   = 8081
		to_port     = 8081
		protocol    = "tcp"
		description = "Kafka schema registry"
		cidr = ["0.0.0.0/0"]
	},
	"http" = {
		from_port   = 80
		to_port     = 80
		protocol    = "tcp"
		description = "HTTP"
		cidr = ["0.0.0.0/0"]
	},
	"http_bis" = {
		from_port   = 8080
		to_port     = 8080
		protocol    = "tcp"
		description = "HTTP"
		cidr = ["0.0.0.0/0"]
	},
	"https" = {
		from_port   = 443
		to_port     = 443
		protocol    = "tcp"
		description = "HTTPS"
		cidr = ["0.0.0.0/0"]
	},
	"openfaas" = {
		from_port   = 31112
		to_port     = 31112
		protocol    = "tcp"
		description = "OpenFaas"
		cidr = ["0.0.0.0/0"]
	},
	"prometheus" = {
		from_port   = 9090
		to_port     = 9090
		protocol    = "tcp"
		description = "prometheus"
		cidr = ["0.0.0.0/0"]
	},
	"kong_ui" = {
		from_port   = 32444
		to_port     = 32444
		protocol    = "tcp"
		description = "kong_ui"
		cidr = ["0.0.0.0/0"]
	},
	"grafana" = {
		from_port   = 3000
		to_port     = 3000
		protocol    = "tcp"
		description = "grafana"
		cidr = ["0.0.0.0/0"]
	},
	"postgres" = {
		from_port   = 5432
		to_port     = 5432
		protocol    = "tcp"
		description = "port for postgres DB"
		cidr = ["0.0.0.0/0"]
	},
	"docker-registry" = {
		from_port   = 5000
		to_port     = 5000
		protocol    = "tcp"
		description = "port for Docker registry"
		cidr = ["0.0.0.0/0"]
	},
	"gitlab-registry" = {
		from_port   = 4567
		to_port     = 4567
		protocol    = "tcp"
		description = "gitlab-container-registry"
		cidr = ["0.0.0.0/0"]
	},
	"nexus" = {
		from_port   = 8081
		to_port     = 8081
		protocol    = "tcp"
		description = "nexus"
		cidr = ["0.0.0.0/0"]
	},
	"dns_challenge" = {
		from_port   = 53
		to_port     = 53
		protocol    = "udp"
		description = "port for allowing LetsEncrypt DNS challenges"
		cidr = ["0.0.0.0/0"]
	},
	"elastic" = {
		from_port   = 9200
		to_port     = 9200
		protocol    = "tcp"
		description = "elastic"
		cidr = ["0.0.0.0/0"]
	},
	"elastic_2" = {
		from_port   = 9300
		to_port     = 9300
		protocol    = "tcp"
		description = "elastic"
		cidr = ["0.0.0.0/0"]
	},
	"haproxy" = {
		from_port   = 32700
		to_port     = 32700
		protocol    = "tcp"
		description = "haproxy"
		cidr = ["0.0.0.0/0"]
	},
	"mongo" = {
		from_port   = 27017
		to_port     = 27017
		protocol    = "tcp"
		description = "mongo"
		cidr = ["0.0.0.0/0"]
	},
}

egress_rules = {
	"default" = {
		from_port = 0
		to_port = 0
		protocol = "-1"
		description = ""
		cidr =["0.0.0.0/0"]
	}
}