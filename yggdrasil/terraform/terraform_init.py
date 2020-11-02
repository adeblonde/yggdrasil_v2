import sys
import os
import shutil
from distutils.dir_util import copy_tree
import json
import subprocess
from dotenv import load_dotenv
from yggdrasil.common_tools import *
import hcl

def prepare_ssh_keys(logger, provider, scope, workfolder) :

	""" parse the network.tfvars file of the current scope in order to retrieve the list of ssh keys to create """
	terraform_tfvars_file = os.path.join(workfolder, 'scopes', scope, 'terraform.tfvars')

	if not os.path.exists(terraform_tfvars_file) :
		logger.info('Missing %s file : cannot extract SSH keys name' % terraform_tfvars_file)
		exit()
	
	tf_parts = dict()
	ssh_prefix = ""
	with open(terraform_tfvars_file, 'r') as f :
		terraform_tfvars = hcl.load(f)
		tf_parts = terraform_tfvars['parts']
		ssh_prefix = "_".join([terraform_tfvars['account'], terraform_tfvars['cost_center'], terraform_tfvars['environment']])

	ssh_keys = [ ssh_prefix + '_' + part  for part in tf_parts.keys()]
	# ssh_keys = [ ssh_prefix + '_' + part + '_' + subpart for part, subparts in tf_parts.items() for subpart in subparts]

	os_user = terraform_tfvars['os_user']

	for ssh_key in ssh_keys :
		public_ssh_key_folder = os.path.join(workfolder, 'secrets', 'ssh', scope, 'public')
		public_ssh_key_file = os.path.join(public_ssh_key_folder, ssh_key + ".pub")
		# public_ssh_key_file = os.path.join(public_ssh_key_folder, ssh_key + "_public.pem")
		private_ssh_key_folder = os.path.join(workfolder, 'secrets', 'ssh', scope, 'private')
		private_ssh_key_file = os.path.join(private_ssh_key_folder, ssh_key)
		# private_ssh_key_file = os.path.join(private_ssh_key_folder, ssh_key + '.pem')
		logger.info("Creating SSH key %s" % private_ssh_key_file)
		if (not os.path.exists(private_ssh_key_file)) | (not os.path.exists(public_ssh_key_file)) :
			exec_path = find_exec_path(logger, 'ssh-keygen')
			try :
				command = [exec_path,
					'-t',
					'rsa',
					'-f',
					ssh_key,
					'-N',
					'',
					'-C',
					os_user
				]
				logger.info("Execution of command :\n%s\nin folder %s" % (' '.join(command), private_ssh_key_folder))
				result = subprocess.call(command, cwd=private_ssh_key_folder)
				logger.info("Result of ssh-keygen call : %s" % result)

				created_public_ssh_key = os.path.join(private_ssh_key_folder, ssh_key + '.pub')
				if not os.path.exists(created_public_ssh_key) :
					logger.info("The public key %s has not been created !" % created_public_ssh_key)
					exit()
				logger.info("Moving public key to public keys folder")
				shutil.move(created_public_ssh_key, public_ssh_key_file)
			except :
				logger.info("Error in the execution of ssh-keygen :\n")
		else :
			logger.info("Private and public keys already exist")

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

# def prepare_credentials_gcp(logger, credentials_file, formatted_credentials_file, region):

# 	""" Prepare well-formatted credentials file for AWS """
# 	gcp_creds = load_aws_credentials(logger, credentials_file)

# # 	gcp_creds_str = """
# # export AWS_ACCESS_KEY={}
# # export AWS_SECRET_KEY={}
# # export AWS_DEFAULT_REGION={}
# # """.format(aws_creds['aws_secret_key'], aws_creds[''])

# 	with open(formatted_credentials_file, 'w') as f :
# 			f.write(gcp_creds_str)

def prepare_credentials(logger, credentials_file, provider, scope, workfolder, region, target_provider) :

	logger.info("Prepare credentials file for provider")

	logger.info("Creating secrets folder")
	provider_secrets_folder = os.path.join(workfolder, 'secrets', provider, scope)
	makedir_p(provider_secrets_folder)
	ssh_secrets_folder = os.path.join(workfolder, 'secrets', 'ssh', scope, 'public')
	makedir_p(ssh_secrets_folder)
	ssh_secrets_folder = os.path.join(workfolder, 'secrets', 'ssh', scope, 'private')
	makedir_p(ssh_secrets_folder)

	if os.path.isfile(credentials_file) :
		logger.info("Setting provider credentials file in place")
		# shutil.copyfile(credentials_file, provider_secrets)
		if provider == "aws" :
			logger.info("Setting AWS secrets")
			provider_secrets = os.path.join(provider_secrets_folder, '.env')
			prepare_credentials_aws(logger, credentials_file, provider_secrets, region)
		if provider == "gcp" :
			logger.info("Setting GCP secrets")
			provider_secrets = os.path.join(provider_secrets_folder, 'credentials.json')
			shutil.copyfile(credentials_file, provider_secrets)

			logger.info("Loading GCP credentials content")
			credentials_content = ""
			with open(credentials_file, 'r') as f:
				credentials_content = json.load(f)
			if 'project_id' not in credentials_content.keys() :
				logger.info('Project ID missing in GCP credentials file located in %s' % credentials_file)

			logger.info("Setting gcp provider tf file with credentials content")
			buffer_provider_file_content = ""
			with open(target_provider, 'r') as f :
				buffer_provider_file_content = f.read()
				buffer_provider_file_content = buffer_provider_file_content.replace('CREDENTIALS_FILE', os.path.join('..','..','secrets', provider, scope, 'credentials.json'))
				buffer_provider_file_content = buffer_provider_file_content.replace('PROJECT_ID', credentials_content['project_id'])
				buffer_provider_file_content = buffer_provider_file_content.replace('REGION', region)

			with open(target_provider, 'w') as f :
				f.write(buffer_provider_file_content)

	return

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

def infra_init(logger, provider, scope, workfolder, exec_path, data_path, credentials_file, region, blueprint, upgrade=False) :

	logger.info("Init action")

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

	logger.info("Preparing architecture from blueprint %s" % blueprint)
	source_blueprint_folder = os.path.join(data_path, "libraries", 'blueprints', blueprint)
	if blueprint.split(':')[0] == "local" :
		blueprint = blueprint.split(':')[1]
		if os.path.exists(blueprint) :
			source_blueprint_folder = blueprint
		else :
			logger.info("Provided local blueprint is not a folder")
			exit()
	copy_tree(source_blueprint_folder, target_scope_folder)

	""" setting SSH public keys folder in scope tf file """
	target_terraform_tfvars_file = os.path.join(target_scope_folder, 'terraform.tfvars')
	if os.path.isfile(target_terraform_tfvars_file) :
		buffer_string = ""
		with open(target_terraform_tfvars_file, 'r') as f :
			buffer_string = f.read()
		buffer_string = buffer_string.replace('SCOPE', scope)
		with open(target_terraform_tfvars_file, 'w') as f :
			f.write(buffer_string)

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

	""" we prepare the credentials for the chosen cloud provider """
	prepare_credentials(logger, credentials_file, provider, scope, workfolder, region, target_provider)

	""" we prepare the SSH keys for the scope """
	prepare_ssh_keys(logger, provider, scope, workfolder)

	logger.info("Storing info in .ygg file")
	ygg_state = os.path.join(workfolder, '.ygg')
	if os.path.isfile(ygg_state) :
		ygg_data = dict()
		with open(ygg_state, 'r') as f :
			ygg_data = json.load(f)
			ygg_data['provider'] = provider
	else :
		ygg_data = {'provider':provider}

	with open(ygg_state, 'w') as f :
			json.dump(ygg_data, f)

	return

def infra_action(logger, action, extra_params, provider, scope, workfolder, exec_path, stdout) :

	logger.info("Apply action %s", action)

	env = dict()
	if provider == "aws" :
		env = load_provider_credentials(logger, provider, scope, workfolder)

	tfvars_folder = os.path.join(workfolder, 'scopes', scope, 'modules')

	# print([os.path.join('modules', f[-7:]) for f in os.listdir(tfvars_folder) if (os.path.isfile(os.path.join(tfvars_folder, f)) )])
	if action != "output" :
		tfvars_list = [os.path.join('modules', f) for f in os.listdir(tfvars_folder) if (os.path.isfile(os.path.join(tfvars_folder, f)) & (f[-7:] == '.tfvars'))]
		for tfvars_file in tfvars_list :
			extra_params = ['--var-file=' + tfvars_file] + extra_params

	else :
		if os.path.exists(os.path.dirname(stdout)) :
			stdout = open(stdout, "w")
		else :
			logger.info("Cannot open Terraform output file %s" % stdout)
			exit()

	scope_folder = os.path.join(workfolder, 'scopes', scope)
	try :
		command = [exec_path, action] + extra_params
		logger.info("Execution of command :\n%s\nin folder %s" % (' '.join(command), scope_folder))
		result = subprocess.call(command, env=env, cwd=scope_folder, stdout=stdout)
		logger.info("Result of Terraform call : %s" % result)
	except :
		logger.info("Error in the execution of Terraform :\n")