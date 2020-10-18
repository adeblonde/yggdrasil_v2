import sys
import os
import shutil
from distutils.dir_util import copy_tree
import json
import subprocess
from dotenv import load_dotenv
from yggdrasil.common_tools import *

def prepare_credentials_aws(logger, credentials_file, formatted_credentials_file, region):

	""" Prepare well-formatted credentials file for AWS """
	aws_creds = load_aws_credentials(logger, credentials_file)

	aws_creds_str = """
export AWS_ACCESS_KEY={}
export AWS_SECRET_KEY={}
export AWS_DEFAULT_REGION={}
""".format(aws_creds['aws_secret_key'], aws_creds[''])

	with open(formatted_credentials_file, 'w') as f :
		f.write(aws_creds_str)

def prepare_credentials_azure(logger, credentials_file, formatted_credentials_file, region):

	""" Prepare well-formatted credentials file for AWS """
	azure_creds = load_aws_credentials(logger, credentials_file)

# 	azure_creds_str = """
# export AWS_ACCESS_KEY={}
# export AWS_SECRET_KEY={}
# export AWS_DEFAULT_REGION={}
# """.format(aws_creds['aws_secret_key'], aws_creds[''])

	with open(formatted_credentials_file, 'w') as f :
			f.write(azure_creds_str)

def prepare_credentials_gcp(logger, credentials_file, formatted_credentials_file, region):

	""" Prepare well-formatted credentials file for AWS """
	gcp_creds = load_aws_credentials(logger, credentials_file)

# 	gcp_creds_str = """
# export AWS_ACCESS_KEY={}
# export AWS_SECRET_KEY={}
# export AWS_DEFAULT_REGION={}
# """.format(aws_creds['aws_secret_key'], aws_creds[''])

	with open(formatted_credentials_file, 'w') as f :
			f.write(gcp_creds_str)

def prepare_credentials(logger, credentials_file, provider, scope, workfolder, region) :

	logger.info("Prepare credentials file for provider")

	logger.info("Creating secrets folder")
	provider_secrets_folder = os.path.join(workfolder, 'secrets', provider)
	makedir_p(provider_secrets_folder)

	if os.path.isfile(credentials_file) :
		logger.info("Setting provider credentials file in place")
		provider_secrets = os.path.join(provider_secrets_folder, scope, '.env')
		# shutil.copyfile(credentials_file, provider_secrets)
		if provider == "aws" :
			prepare_credentials_aws(logger, credentials_file, provider_secrets, region)

def load_provider_credentials(logger, provider, scope, workfolder) :

	""" this function check if the credentials of the provider do exist at the right place and format then load them"""
	
	logger.info("Loading provider credentials")

	provider_secrets_folder = os.path.join(workfolder, 'secrets', provider)
	provider_secrets = os.path.join(provider_secrets_folder, scope, '.env')

	if os.path.exists(provider_secrets) :
		logger.info("Setting provider credentials file in place")

		return load_dotenv(provider_secrets)

	else :
		raise Exception("Cannot read credentials file for this provider")

def infra_init(logger, provider, scope, workfolder, exec_path, data_path, credentials_file, region, upgrade=False) :

	logger.info("Init action")

	prepare_credentials(logger, credentials_file, provider, scope, workfolder, region)

	logger.info("Creating Terraform modules")
	tf_modules_folder = os.path.join(workfolder, 'terraform')
	makedir_p(tf_modules_folder)

	""" we walk through the list of Terraform modules in the package's libraries and copy them """
	libraries_tf_folder = os.path.join(data_path, 'libraries', 'terraform', 'modules')
	# for root, dirs, files in os.walk(libraries_tf_folder) :
	for module_name in os.listdir(libraries_tf_folder) :
		""" dealing with common Terraform modules """
		module_dir = os.path.join(libraries_tf_folder, module_name)
		makedir_p(os.path.join(tf_modules_folder, module_name))

		if provider in os.listdir(module_dir) :
			""" copying main.tf and outputs.tf """
			for tf_file in ['main.tf', 'outputs.tf'] :
				source_file = os.path.join(module_dir, provider, tf_file)
				dest_file = os.path.join(tf_modules_folder, module_name, tf_file)
				if os.path.isfile(source_file) :
					shutil.copyfile(source_file, dest_file)
				else :
					logger.info("Error : file %s missing in package source", source_file)
					
			""" copying variables.tf (common for all providers) """
			source_file = os.path.join(module_dir, 'variables.tf')
			dest_file = os.path.join(tf_modules_folder, module_name, 'variables.tf')
			if os.path.isfile(source_file) :
				shutil.copyfile(source_file, dest_file)
			else :
				logger.info("Error : file %s missing in package source", source_file)
		
	logger.info("Creating scopes folder")
	source_scopes_folder = os.path.join(data_path, 'libraries', 'terraform', 'scopes')
	target_scope_folder = os.path.join(workfolder, 'scopes', scope)

	logger.info("Creating scope %s folder tree" % scope)
	makedir_p(target_scope_folder)
	copy_tree(source_scopes_folder, target_scope_folder)

	""" we get the 'provider.tf' file specific to the chosen provider """
	logger.info("Setting scope provider")
	source_provider = os.path.join(data_path, 'libraries', 'terraform', 'providers', provider + '.tf')
	target_provider = os.path.join(workfolder, 'scopes', scope, 'provider.tf')
	shutil.copy(source_provider, target_provider)

	""" we get the terraform variable file providing the name mappings for the chosen provider """
	logger.info("Setting scope provider specific resources' names")
	source_resources = os.path.join(data_path, 'libraries', 'terraform', 'resources', provider + '.tfvars')
	target_resources = os.path.join(workfolder, 'scopes', scope, 'resources.auto.tfvars')
	shutil.copy(source_resources, target_resources)

	logger.info("Storing info in .ygg file")
	ygg_state = os.path.join(workfolder, '.ygg')
	if os.path.isfile(ygg_state) :
		ygg_data = dict()
		with open(ygg_state, 'w') as f :
			ygg_data = json.load(f)
			ygg_data['provider'] = provider
	else :
		ygg_data = {'provider':provider}

	with open(ygg_state, 'r') as f :
			json.dump(ygg_data, f)

	return

def infra_action(logger, action, extra_params, exec_path, provider, scope, workfolder) :

	logger.info("Apply action %s", action)

	env = load_provider_credentials(logger, provider, scope, workfolder)

	tfvars_folder = os.path.join(workfolder, 'scope', scope, 'modules')

	tfvars_list = [f for f in os.listdir(tfvars_folder) if (os.path.isfile(os.path.join(tfvars_folder, f) & f[-5:] == '.tfvars'))]
	for tfvars_file in tfvars_list :
		extra_params += ['--var-file=' + os.path.join(tfvars_folder, tfvars_file)]

	try :
		command = [exec_path, action] + extra_params
		result = subprocess.call(command, env=env)
		logger.info("Result of ansible call : %s" % result)
	except :
		logger.info("Error in the execution of Terraform :\n")