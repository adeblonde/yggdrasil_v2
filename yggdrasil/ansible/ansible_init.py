import json
import os
from yggdrasil.common_tools import makedir_p
import shutil
import subprocess
import yaml

def config_init(logger, provider, scope, workfolder, data_path) :

	""" adding ansible.cfg to scope """
	source_ansible_cfg = os.path.join(data_path, 'libraries', 'ansible', 'ansible.cfg')
	target_ansible_cfg = os.path.join(workfolder, 'inventories', scope, 'ansible.cfg')
	shutil.copyfile(source_ansible_cfg, target_ansible_cfg)

	""" create host file and ssh config file """

	logger.info("Parsing Terraform output file")

	inventory_folder = os.path.join(workfolder, 'inventories', scope)
	terraform_output_file = os.path.join(inventory_folder, 'terraform_output.json')

	""" check if Terraform output file does exist """
	if not os.path.exists(terraform_output_file) :
		raise Exception("Terraform output file %s does not exist" % terraform_output_file)

	with open(terraform_output_file, "r") as f :
		tf_outputs = json.loads(f.read())

	""" we create a dictionary of all VMs in order to gather their connection properties """
	machines = dict()

	if 'vms' not in tf_outputs.keys() :
		raise Exception("Missing list of VMs")

	machines = tf_outputs['vms']['value']
	requested_networks = tf_outputs['requested_networks']['value']

	subnet_bastion = dict()

	for machine_name, machine in machines.items() :
		for param in ["subnet", "network_name", "public_ip", "ssh_key", "group", "user"] :
			# print(machine.keys())
			if param not in machine.keys() :
				logger.info("Missing %s info in machine %s" % (param, machine_name))
				exit()
		if machine["group"] == "bastion" :
			subnet_bastion[machine["subnet"]] = machine_name

	for machine_name, machine in machines.items() :
		# machine_subnet = machine["subnet"]
		# print(requested_networks[machine["network_name"]])
		# print(machine["subnet"])
		machine_escape_subnet = requested_networks[machine["network_name"]]["private_subnets_escape_public_subnet"]
		# print(machine_subnet)
		# print(subnet_bastion)
		if machine_escape_subnet in subnet_bastion.keys() :
			machine_bastion = subnet_bastion[machine_escape_subnet]
			machines[machine_name]["access_ip"] = machines[machine_bastion]["public_ip"]

	# print(machines)

	# for key, value in tf_outputs['vms']['value'] :
	# 	machines[]

	# for key, value in tf_outputs['private_ips'] :
	# 	machines[key] = {
	# 		'private_ip' : value,
	# 	}
	# 	for param in ["subnet", "network", "public_ip", "ssh_key", "group", "user"] :
	# 		if key in tf_outputs["machine_" + param] :
	# 			machines[key][param] = tf_outputs["machine_" + param][key]
	# 		if key in tf_outputs["subnet"] :
	# 			machine_subnet = tf_outputs["subnets"][key]
	# 			if machine_subnet in tf_outputs["private_subnets_escape_public_subnet"].keys() :
	# 				escape_public_subnet = tf_outputs["private_subnets_escape_public_subnet"][machine_subnet]
	# 				if escape_public_subnet in tf_outputs["public_subnet_bastion"] :
	# 					bastion_name = tf_outputs["public_subnet_bastion"][escape_public_subnet]
	# 					if bastion_name in tf_outputs["machine_public_ip"] :
	# 						machines[key]["ssh_bastion"] = tf_outputs["machine_public_ip"][bastion_name]

	""" we create sets of machines according to their group name, network, and subnet belonging """
	machines_per_category = dict()
	categories = ["subnet", "network_name", "group"]
	for category in categories :
		machines_per_category[category] = dict()
		values_for_category = list(set([val[category] for val in machines.values()]))
		for elt in values_for_category :
			# eligible_machines = [machine for machine in machines if category in machine.keys()]
			machines_per_category[category][elt] = [machine for _, machine in machines.items() if machine[category] == elt ]

	""" we write the list of hosts, grouped by categories, into envt.hosts file """
	print(machines_per_category)
	output_string = """[all:vars]
ansible_python_interpreter=/usr/bin/python3"""

	for category in categories :
		for elt, machine_list in machines_per_category[category].items() :
			output_string += "\n\n[{}]".format(elt)
			for machine in machine_list :
				if machine["group"] == "bastion" :
					output_string += "\n{}".format(machine["public_ip"])
				else :
					output_string += "\n{}".format(machine["private_ip"])

	host_file = os.path.join(workfolder, 'inventories', scope, 'envt.hosts')

	""" we write individual access to the machines """
	for machine_name, machine in machines.items() :
		output_string += "\n\n[{}]".format(machine_name)
		if machine["group"] == "bastion" :
			output_string += "\n{}".format(machine["public_ip"])
		else :
			output_string += "\n{}".format(machine["private_ip"])

	with open(host_file, "w") as f :
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
		"container_registry" : [
			"container_registry_url"
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
		if paas in tf_outputs.keys() :
			output_string += "[{}]\n".format(paas)
			paas_dict = tf_outputs[paas]['value']
			# for paas_property in paas_services[paas] :
			# 	# print(tf_outputs.keys())
			# 	print(paas_property)
			# 	print(tf_outputs[paas]['value'])
			# 	paas_properties_output = tf_outputs[paas]['value']
			# 	if paas_property in paas_properties_output.keys() :
			# 		print(paas_property)
			# 	for paas_instance_name, paas_instance_properties in paas_properties_output[paas_property] :
			# 		if paas_instance_name not in paas_dict.keys() :
			# 			paas_dict[paas_instance_name] = {
			# 				paas_property : paas_instance_property
			# 			}
			# 		else :
			# 			paas_dict[paas_instance_name][paas_instance_property] = paas_instance_property

			for paas_instance, paas_properties in paas_dict.items() :
				output_string += "{} = {}".format(paas + '_name', paas_instance)
				for paas_property_name, paas_property_value in paas_properties.items() :
					if paas_property_name in paas_services[paas] :
						output_string += " {} = {}".format(paas_property_name, paas_property_value)
				output_string += "\n"

			output_string += "\n\n"

	paas_file = os.path.join(workfolder, 'inventories', scope, 'paas.ini')

	with open(paas_file, "w") as f :
		f.write(output_string)


	logger.info("Creating SSH config file")

	output_string_common = ""
	output_string_bastion = ""

	for _, machine in machines.items() :
		if machine["group"] != "bastion" :
			output_string_common += "# {}\nHost {}\n ProxyCommand ssh -F ssh.cfg -W %h:%p {}\n User {}\n IdentityFile {}\n\n".format(machine["group"], machine['private_ip'], machine['access_ip'], machine['user'], os.path.join(workfolder, 'secrets', 'ssh', scope, 'private', machine['ssh_key']))
		else :
			output_string_bastion += "# {}\nHost {}\n Hostname {}\n User {}\n IdentityFile {}\n\n".format(machine["group"], machine['public_ip'], machine['public_ip'], machine['user'], os.path.join(workfolder, 'secrets', 'ssh', scope, 'private', machine['ssh_key']))

	output_string_footer = """
# multiplexing SSH
Host *
 ControlMaster   auto
 ControlPath     ~/.ssh/mux-%r@%h:%p
 ControlPersist  15m
"""

	ssh_config_file = os.path.join(workfolder, 'inventories', scope, 'ssh.cfg')

	with open(ssh_config_file, 'w') as f :
		f.write(output_string_bastion + output_string_common + output_string_footer)

def config_apply(logger, exec_path, provider, scope, workfolder) :

	logger.info("Apply configuration")

	configuration_file = os.path.join(workfolder, 'scopes', scope, 'configuration.yml')

	if not os.path.exists(configuration_file) :
		raise Exception("Configuration file for scope %s does not exist", scope)

	logger.info("Loading configuration commands to execute")
	configuration_commands = []
	with open(configuration_file, 'r') as f :
		configuration_commands = yaml.load(f, Loader=yaml.FullLoader)

	if 'operations' in configuration_commands.keys() :
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
				if 'extra-vars' in operation.keys() :
					if type(operation['extra-vars']) is list :
						for param in operation['extra-vars'] :
							ansible_command += ['--extra-vars', param]
			try :
				command = [exec_path, action] + extra_params
				result = subprocess.call(command, env=env)
				logger.info("Result of Ansible call : %s" % result)
			except :
				logger.info("Error in the execution of Terraform :\n")
