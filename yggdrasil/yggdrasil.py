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
@click.argument('action', default='status')
@click.argument('--configuration-file','-f', default='./yggdrasil_config.yml')
@click.option('--parameters','-p', default=None, help='YAML file storing parameters to set in the configuration file')
@click.option('--workfolder','-w', default='.',help='Location of the working folder that will be created with temporary file, name after \'config_name\'')
def ygg(action, configuration_file, parameters, workfolder) :

    """ we execute the run options with the provided arguments """
    run(action, configuration_file, workfolder, parameters)

def run(action, configuration_file, workfolder, params, variable=None, dryrun=False, shutdownatend=False) :

	""" the run function is separated from the main CLI function ygg, for modularity purposes """

	""" main yggdrasil function """
	print("Begin execution of Yggdrasil!")

	""" create work folder """
	work_dir = workfolder
	makedir_p(work_dir)

	""" init logger """
	logger = create_logger(join(work_dir,'ygg.log'))

	""" parse config file """
	config = set_parameters(logger, configuration_file, params, variable)
