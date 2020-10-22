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
from .common_tools import *
from .terraform import terraform_init
from .ansible import ansible_init

DATA_PATH = pkg_resources.resource_filename('yggdrasil', '.')


def find_exec_path(logger) :

	""" this function returns the path to the Terraform executable """
	terraform_path = shutil.which('terraform')

	return terraform_path

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
@click.argument('stage')
@click.argument('action')
@click.option('--credentials','-c', default='credentials.json', help='Location of the credentials file for the chosen cloud provider')
@click.option('--provider','-p', default='aws', help='cloud provider name, currently either "aws", "azure" or "gcp"')
@click.option('--scope','-s', default='dev', help='architecture scope')
@click.option('--workfolder','-w', default='.', help='Location of the working folder that will be created with temporary file, name after \'config_name\'')
@click.option('--region','-r', default='us-east-1', help='Location of the working folder that will be created with temporary file, name after \'config_name\'')
@click.option('--blueprint','-r', default=None, help='Name of a cloud architecture blueprint from Yggdrasil\'s library for bootstrapping')
def ygg(stage, action, provider, scope, workfolder, credentials, region, blueprint) :

    """ we execute the run options with the provided arguments """
    run(stage, action, provider, scope, workfolder, credentials, region)
    # run(action, configuration_file, workfolder, parameters)

# def run(step, action, configuration_file, workfolder, params, variable=None, dryrun=False, shutdownatend=False) :
def run(stage, action, provider, scope, workfolder, credentials_file, region, blueprint) :

	""" the run function is separated from the main CLI function ygg, for modularity purposes """

	""" main yggdrasil function """
	print("Begin execution of Yggdrasil!")

	""" create work folder """
	work_dir = workfolder
	makedir_p(work_dir)

	""" init logger """
	logger = create_logger(join(work_dir,'ygg.log'))

	""" parse config file """
	# config = set_parameters(logger, configuration_file, params, variable)

	""" execute stage """
	if stage == "infra" :
		infra(logger, action, provider, scope, workfolder, credentials_file, region, blueprint)
	if stage == "config" :
		config(logger, action, provider, scope, workfolder)

def infra(logger, action, provider, scope, workfolder, credentials_file, region, blueprint) :

	logger.info("Entering stage infra")

	""" get Terraform executable """
	try :
		exec_path = find_exec_path('terraform')
	except :
		logger.info("Terraform executable not found")

	""" if needed, initialize credentials and Terraform folder tree """
	if action == "init" :
		if not os.path.exists(credentials_file) :
			logger.info("Missing credentials file at location %s, stopping program" % credentials_file)
			exit()
		terraform_init.infra_init(logger, provider, scope, workfolder, exec_path, DATA_PATH, credentials_file, region, blueprint)

	""" infra_action executes the 'action' infra function """
	extra_params = []
	if action == "output" :
		inventory_folder = os.path.join(workfolder, 'inventories', scope)
		makedir_p(inventory_folder)
		terraform_output_file = os.path.join(inventory_folder, 'terraform_output.json')
		extra_params = ["output", "-json", ">", terraform_output_file]
	
	terraform_init.infra_action(logger, action, extra_params, provider, scope, workfolder, exec_path)

def config(logger, action, provider, scope, workfolder) :

	logger.info("Entering stage config")

	""" get Ansible executable """
	try :
		exec_path = find_exec_path('ansible-playbook')
	except :
		logger.info("ansible-playbook executable not found")

	if action == "init" :
		ansible_init.config_init(logger, provider, scope, workfolder)

	if action == "apply" :
		ansible_init.config_apply(logger, exec_path, provider, scope, workfolder)

	