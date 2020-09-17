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

DATA_PATH = pkg_resources.resource_filename('yggdrasil', '.')

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
@click.argument('--provider','-c', default='auto', help='cloud provider name, currently either "aws", "azure" or "gcp"')
@click.argument('--scope','-s', default='dev', help='architecture scope')
# @click.argument('--configuration-file','-f', default='./yggdrasil_config.yml')
# @click.option('--parameters','-p', default=None, help='YAML file storing parameters to set in the configuration file')
@click.option('--workfolder','-w', default='.',help='Location of the working folder that will be created with temporary file, name after \'config_name\'')
# def ygg(action, configuration_file, parameters, workfolder) :
def ygg(stage, action, provider, scope, workfolder) :

    """ we execute the run options with the provided arguments """
    run(stage, action, provider, scope, workfolder)
    # run(action, configuration_file, workfolder, parameters)

# def run(step, action, configuration_file, workfolder, params, variable=None, dryrun=False, shutdownatend=False) :
def run(stage, action, provider, scope, workfolder) :

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
	stage(logger, action, provider, scope, workfolder)

def infra(logger, action, provider, scope, workfolder) :

	logger.info("Entering stage infra")

	""" infra_action executes the 'action' infra function """
	terraform_init.action(logger, provider, scope, workfolder, DATA_PATH)
	
