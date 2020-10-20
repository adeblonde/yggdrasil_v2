import json
import os
from yggdrasil.common_tools import makedir_p
import shutil
import subprocess
import yaml

def config_init(logger, provider, scope, workfolder) :

	""" create host file and ssh config file """

	logger.info("Parsing Terraform output file")

	terraform_output_file = os.path.join(inventory_folder, 'terraform_output.json')

	""" check if Terraform output file does exist """
	if not os.path.exists(terraform_output_file) :
		raise Exception("Terraform output file %s does not exist" % terraform_output_file)

	with open(terraform_output_file, "r") as f :
		tf_outputs = json.loads(f.read())

	""" we create a dictionary of all VMs in order to gather their connection properties """
	machines = dict()

	if 'private_ips' not in tf_outputs.keys() :
		raise Exception("Missing list of VMs private IPs")

	for key, value in tf_outputs['private_ips'] :
		machines[key] = {
			'private_ip' : value,
		}
		for param in ["subnet", "network", "public_ip", "ssh_key", "short_name", "group", "user"] :
			if key in tf_outputs["machine_" + param] :
				machines[key][param] = tf_outputs["machine_" + param][key]
			if key in tf_outputs["subnet"] :
				machine_subnet = tf_outputs["subnets"][key]
				if machine_subnet in tf_outputs["private_subnets_escape_public_subnet"].keys() :
					escape_public_subnet = tf_outputs["private_subnets_escape_public_subnet"][machine_subnet]
					if escape_public_subnet in tf_outputs["public_subnet_bastion"] :
						bastion_name = tf_outputs["public_subnet_bastion"][escape_public_subnet]
						if bastion_name in tf_outputs["machine_public_ip"] : 
							machines[key]["ssh_bastion"] = tf_outputs["machine_public_ip"][bastion_name]

	""" we create sets of machines according to their group name, network, and subnet belonging """
	machines_per_category = dict()
	categories = ["subnets", "networks", "groups"] :
	for category in categories :
		machines_per_category[category] = dict()
		for elt in tf_outputs[category] :
			eligible_machines = [machine for machine in machines if category[:-1] in machine.keys()]
			machines_per_category[category][elt] = [machine for machine in eligible_machines if machine[category[:-1]] == elt ]

	""" we write the list of hosts, grouped by categories, into envt.hosts file """

	output_string = """[all:vars]
ansible_python_interpreter=/usr/bin/python3"""

	for category in categories :
		for elt, machine_list in machines_per_category[category] :
			output_string += "\n\n[{}]".format(elt)
			for machine in machine_list :
				if machine["group"] == "bastion" :
					output_string += "\n{}".format(machine["public_ip"])
				else :
					output_string += "\n{}".format(machine["private_ip"])

	host_file = os.path.join(workfolder, 'inventories', scope, 'envt.hosts')

	""" we write individual access to the machines """
	for machine_name, machine in machines :
		output_string += "\n\n[{}]".format(machine_name)
		if machine["group"] == "bastion" :
			output_string += "\n{}".format(machine["public_ip"])
		else :
			output_string += "\n{}".format(machine["private_ip"])

	with open(host_file, "r") as f :
		f.write(output_string)

	""" we create a dictionary of all PaaS addresses """
	output_string = ""

	paas_services = {
		"kubernetes_cluster" : [
			"kubernetes_cluster_endpoint",
			"kubernetes_cluster_id",
			"kubernetes_cluster_certificate_authority"
		],
		"kafka_cluster" : [
			"kafka_cluster_version",
			"kafka_bootstrap_brokers",
			"kafka_zookeeper_connect_string",
			"kafka_replica_count"
		],
		"docker_registry" : [
			"registry_url"
		],
		"storage" : [
			"storage_name"
		],
		"mq" : [
			"mq_stream_id"
		],
		"yarn_cluster" : [
			"yarn_master_ip"
		],
		"function" : [
			"function_address"
		]
	}

	logger.info("Looking for PaaS services in Terraform output")
	
	for paas in paas_services.keys() :
		output_string += "[{}]\n".format(paas)
		paas_dict = dict()
		for paas_property in paas_services[paas] :
			if paas_property in terraform_output_file.keys() :
				for paas_instance_name, paas_instance_property in terraform_output_file[paas_property] :
					if paas_instance_name not in paas_dict.keys() :
						paas_dict[paas_instance_name] = {
							paas_property : paas_instance_property
						}
					else :
						paas_dict[paas_instance_name][paas_instance_property] = paas_instance_property

		for paas_instance, paas_properties in paas_dict :
			output_string += "{} = {}".format(paas + '_name', paas_instance)
			for paas_property_name, paas_property_value in paas_property :
				output_string += " {} = {}".format(paas_property_name, paas_property_value)
			output_string += "\n"

		output_string += "\n\n"

	paas_file = os.path.join(workfolder, 'inventories', scope, 'paas.ini')

	with open(paas_file, "r") as f :
		f.write(output_string)


	logger.info("Creating SSH config file")

	output_string_common = ""
	output_string_bastion = ""

	for machine in machines :
		if machine["group"] == "bastion" :
			output_string_common += "# {}\nHost {}\n ProxyCommand ssh -F ssh.cfg -W %h:%p {}\n User {}\n IdentityFile {}.pem\n\n".format(machine["group"], machine['private_ip'], machine['ssh_bastion'], machine['user'], os.path.join(workfolder, 'credentials', 'ssh', 'private', machine['ssh_key']))
		else :
			output_string_bastion += "# {}\nHost {}\n Hostname {}\n User {}\n IdentityFile {}.pem\n\n".format(machine["group"], machine['public_ip'], machine['ssh_bastion'], machine['user'], os.path.join(workfolder, 'credentials', 'ssh', 'private', machine['ssh_key']))

	output_string_footer = """
# multiplexing SSH
Host *
 ControlMaster   auto
 ControlPath     ~/.ssh/mux-%r@%h:%p
 ControlPersist  15m
"""

	ssh_config_file = os.path.join(workfolder, 'inventories', scope, 'ssh.cfg')

	with open(ssh_file, 'w') as f :
		f.write(output_string_bastion + output_string_target + output_string_footer)

def config_apply(logger, exec_path, provider, scope, workfolder) :

	logger.info("Apply configuration %s", action)

	configuration_file = os.path.join(workfolder, 'scopes', scope, 'configuration.yml')

	if not os.path.exists(configuration_file) :
		raise Exception("Configuration file for scope %s does not exist", scope)

	logger.info("Loading configuration commands to execute")
	configuration_commands = []
	with open(configuration_file, 'r') as f :
		configuration_commands = yaml.load(f, Loader=yaml.FullLoader)

	if 'operations' in configuration_commands.keys()
		for operation in configuration_commands["operations"] :
			ansible_command = [exec_path,
				'-i', os.path.join(workfolder, 'inventories', scope, 'envt.hosts')
			]
			if 'action' in operation.keys() : 
				if 'target' in operation.keys() :
					ansible_command += [
						'--limit', operation['target']
					]
				ansible_command += [
					os.path.join(workfolder, 'ansible', 'playbooks', operation + 'yml')
				]
				if 'extra-vars' in operation.keys()
					if type(operation['extra-vars']) is list :
						for param in operation['extra-vars']]
							ansible_command += ['--extra-vars', param]
			try :
				command = [exec_path, action] + extra_params
				result = subprocess.call(command, env=env)
				logger.info("Result of Ansible call : %s" % result)
			except :
				logger.info("Error in the execution of Terraform :\n")
