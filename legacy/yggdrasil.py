from .common_tools import *
from .terraform.aws import *
from .terraform.tf_run import run_terraform, destroy_terraform
from .ansible_resources.ansible_setting import *
from .security.secure_credentials import *
# from ansible_templates import *
import os
import sys
import yaml
import fileinput
import shutil
import pkg_resources
import copy
import json
import click
from os.path import join

import pdb

DATA_PATH = pkg_resources.resource_filename('yggdrasil', '.')

ami2user = {
	'ami-2a7d75c0' : 'ubuntu'
}

def set_parameters(logger, configfile, params, variable=None) :

	""" this function extract a configuration from a YAML config file and set the unset parameters using a params file """
	with open(configfile) as f :
		config = f.read()
		config_params = yaml.load(config)['parameters']

	# logger.info("Initial config : %s" % config)

	parameters = dict()

	if params is not None :
		with open(params) as f :
			parameters = yaml.load(f.read())['parameters']
			logger.info("Parameters loaded : %s" % parameters)
			# parameters = json.load(f)

	if variable is not None :
		for key, value in variable :
			parameters[key] = value

	for param in parameters.keys() :
		# if param in config_params.keys():
		if param in config_params :
			config = config.replace(param, parameters[param])

	# logger.info("Set config : %s" % config)

	return yaml.load(config)

@click.command()
@click.argument('configfile', default='./yggdrasil_config.yml')
# @click.argument('configfile', default='./yggdrasil_config.yml',help='Path to yggdrasil configuration file')
@click.option('--parameters','-p', default=None,help='YAML file storing parameters to set in the configuration file')
@click.option('--shutdownatend','-s', default=False,help='Do you want to shutdown host machines after execution of all jobs ?')
@click.option('--dryrun','-d', default=False,help='Execute a dry run of the Terraform configuration, Ansible jobs won\'t be executed')
@click.option('--workfolder','-w', default='.',help='Location of the working folder that will be created with temporary file, name after \'config_name\'')
def ygg(configfile, workfolder, parameters, variable=None, dryrun=False, shutdownatend=False) :

	""" we execute the run options with the provided arguments """
	run(configfile, workfolder, parameters, variable, dryrun, shutdownatend)

# @click.command()
# @click.argument('configfile', help='Yggdrasil YAML configuration file to set')
# @click.option('--output','-o', help='Yggdrasil YAML configuration file set')
# @click.option('--params','-f', help='JSON file with all the parameters to set in the Yggdrasil\'s configuration file')
# @click.option('--variable','-v', type=(unicode, unicode), multiple=True)
# def ygg_config(configfile, output, params, variable):

# 	""" this function is used to set the variables in an Yggdrasil's unset configuration file """
# 	if output is None :
# 		output = os.getcwd()
# 		output_name = os.path.basename(configfile)
# 		output_name = 'set_' + output_name
# 		output = join(output, output_name)

# 	output_folder = os.path.dirname(output)
# 	makedir_p(output_folder)

# 	config = set_parameters(configfile, params, variable)

# 	with open(output, 'w') as f :
# 		f.write(config)

def run(configfile, workfolder, params, variable=None, dryrun=False, shutdownatend=False) :

	""" the run function is separated from the main CLI function ygg, for modularity purposes """

	""" main yggdrasil function """
	print("Begin execution of Yggdrasil!")

	""" create work folder """
	work_dir = workfolder
	makedir_p(work_dir)

	""" init logger """
	logger = create_logger(join(work_dir,'ygg.log'))

	""" parse config file """
	config = set_parameters(logger, configfile, params, variable)

	""" Terraform part """
	logger.info("Terraform part")

	


	""" init terraform config file """
	tf_config = ''

	""" prepare Terraform config file """
	logger.info("Configuration content : %s" %config)
	# logger.info("Configuration content : %s" % config['config_name'])
	tf_cloud_creds = ''
	ansible_cloud_creds = ''
	for provider in config['infrastructure']['providers'] :
		provider = provider['provider']

		if provider['provider_name'] == 'aws' :

			logger.info("Creating encrypted Ansible AWS credentials file")
			auth_dir = config['ansible_resources']['vault_dir']
			makedir_p(auth_dir)
			aws_encrypted_creds = os.path.join(auth_dir, config['config_name'] + '_aws_encrypted.yml')

			if config['ansible_resources']['do_encrypt'] == True :
				secure_ansible_aws(logger, auth_dir, provider, aws_encrypted_creds, config['ansible_resources']['vault_password_file'])
				logger.info("Successfully created encrypted Ansible creds file %s" % aws_encrypted_creds)

			ansible_cloud_creds = os.path.join(auth_dir, aws_encrypted_creds)

			logger.info("Creating Terraform variables file storing AWS credentials")
			auth_dir = config['terraform_resources']['credentials_dir']
			tf_aws_creds = os.path.join(auth_dir, config['config_name'] + '_aws_creds.tfvars')
			secure_tf_aws(logger, auth_dir, provider, tf_aws_creds)
			logger.info("Successfully created variables file %s" % tf_aws_creds)
			tf_cloud_creds = tf_aws_creds

			logger.info("Configuring Terraform file")
			tf_config = terraform_set_aws(logger, DATA_PATH, work_dir, provider)

	""" check for special options """
	
	""" Destroy infrastructure """
	if config['options']['destroy'] == True :
		logger.info("Destroy infrastructure")
		destroy_terraform(logger, work_dir, tf_cloud_creds)

	with open(join(work_dir, config['config_name'] + '.tf'), 'w') as f :
		f.write(tf_config)

	""" run Terraform """
	logger.info("Run Terraform")
	run_terraform(logger, work_dir, config, tf_cloud_creds, dryrun)
	
	""" Ansible part """
	logger.info("Ansible part")

	""" we parse the .tfstate file to gather public IPs addresses """
	logger.info("Parsing .tfstate")
	host_ips, host_usernames, group_hosts = gather_ips(work_dir, ami2user, logger)

	if len(host_ips) == 0 :
		logger.info("No hosts available, exit")
		return

	""" create Ansible config tree """
	logger.info("Creating Ansible config tree")
	ansible_dir, ansible_production_dir, ansible_roles_dir = create_config_tree(logger, work_dir)

	""" create hosts file """
	logger.info("Creating Ansible hosts file")
	production_hosts_path = create_host_file(logger, config, host_ips, host_usernames, group_hosts, ansible_production_dir)

	""" set an SSH connection that will accept unknown hosts """	
	logger.info("Setting SSH connection""")
	ssh = set_ssh_connection()

	# """ sending data to hosts """
	# logger.info("Sending data to remote hosts")
	# scp_data(ssh, logger, host_ips, group_hosts, host_usernames, config, 'sending')

	""" collect all ansible playbooks paths """
	logger.info("Collecting all ansible playbooks paths")
	modules_playbooks = join(DATA_PATH, 'playbooks')
	playbooks_folder = [modules_playbooks]
	playbooks_path = collect_playbooks_paths(logger, config, playbooks_folder)

	""" collecting all synchronous jobs """
	logger.info("Collecting all synchronous jobs")
	main_ansible_path = collect_synchronous_jobs(logger, config, ansible_roles_dir, ansible_dir, playbooks_path, ansible_cloud_creds)

	""" Execution of synchronous jobs """
	logger.info("Executing Ansible synchronous tasks")
	try :
		command = ['/usr/bin/ansible-playbook', '-i', production_hosts_path, main_ansible_path,
		'--vault-password-file', config['ansible_resources']['vault_password_file'],
		'--key-file', config['infrastructure']['private_ssh_key_path']]
		logger.info("Executing ansible with command %s" % (' '.join(command)))
		result = subprocess.call(command, env={'ANSIBLE_HOST_KEY_CHECKING':'False'})
		logger.info("Result of ansible call : %s" % result)
	except :
		logger.info("Problem in the execution of ansible playbooks")

	""" implementing workers pool jobs """
	logger.info("Collecting Ansible asynchronous tasks")
	processes = prepare_pool_jobs(logger, config, ansible_dir, production_hosts_path, playbooks_path, group_hosts, ansible_cloud_creds)

	logger.info("Executing Ansible asynchronous tasks")
	for p in processes :
		p.start()

	for p in processes :
		p.join()

	""" receiving from to hosts """
	logger.info("Receiving data from remote hosts")
	scp_data(ssh, logger, host_ips, group_hosts, host_usernames, config, 'receiving')

if __name__ == "__main__" :
	run(sys.argv[1], sys.argv[2])