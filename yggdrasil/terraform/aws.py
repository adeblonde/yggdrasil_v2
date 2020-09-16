import copy
import os
from os.path import join
from yggdrasil.common_tools import load_aws_credentials

def terraform_set_aws(logger, DATA_PATH, work_dir, aws_config) : 

	""" this function parse the AWS credentials file and create a Terraform .tf file from the configuration provided """
	# cloud_creds = load_aws_credentials(logger, config['infrastructure']['credentials_file'])

	tf_resources = join(DATA_PATH, 'terraform', 'aws')

	# """ set the AWS config file """
	# with open(join(tf_resources, 'aws_config_template'), 'r') as f_read, open(join(work_dir, 'config'), 'w') as f_write :
	# 	aws_config_str = f_read.read()
	# 	aws_config_str = aws_config_str.replace('default',config['infrastructure']['profile'])
	# 	aws_config_str = aws_config_str.replace('AWS_REGION',config['infrastructure']['region'])
	# 	f_write.write(aws_config_str)

	# """ set the AWS credentials file """
	# with open(join(tf_resources, 'aws_credentials_template'), 'r') as f_read, open(join(work_dir, 'credentials'), 'w') as f_write :
	# 	aws_config_str = f_read.read()
	# 	aws_config_str = aws_config_str.replace('AWS_ACCESS_KEY',cloud_creds['aws_access_key_id'])
	# 	aws_config_str = aws_config_str.replace('AWS_SECRET_KEY',cloud_creds['aws_secret_key'])
	# 	f_write.write(aws_config_str)

	""" create the terraform config file """
	logger.info("Creating the Terraform config file")
	
	with open(join(tf_resources, 'aws_header.tf'), 'r') as f :
		tf_header = f.read()
	
	with open(join(tf_resources, 'aws_security_group.tf'), 'r') as f :
		tf_security = f.read()

	with open(join(tf_resources, 'aws_instance.tf'), 'r') as f :
		tf_instance = f.read()

	# tf_header = tf_header.replace('AWS_ACCESS_KEY',cloud_creds['aws_access_key_id'])
	# tf_header = tf_header.replace('AWS_SECRET_KEY',cloud_creds['aws_secret_key'])
	# tf_header = tf_header.replace('AWS_REGION',config['infrastructure']['region'])

	tf_config = tf_header + '\n\n' + tf_security
	# tf_config = ''

	for model in aws_config['machines'] :
		model = model['machine']
		current_model = copy.deepcopy(tf_instance)
		current_model = current_model.replace('NUMBER', str(model['number']))
		current_model = current_model.replace('INSTANCE_NAME', str(model['name']) + "_${count.index}")
		current_model = current_model.replace('HOST_USERNAME', str(model['user']))
		current_model = current_model.replace('NAME', str(model['name']))
		current_model = current_model.replace('SSH_KEY', aws_config['ssh_key'])
		current_model = current_model.replace('AMI', model['aws_specs']['AMI'])
		current_model = current_model.replace('TYPE', model['aws_specs']['type'])
		current_model = current_model.replace('SECURITY_GROUP', model['aws_specs']['security_group'])
		""" let's set the groups """
		group_str = ""
		if 'groups' in model.keys() :
			for group in model['groups'] :
				group_str += "Group_" + group + " = \"True\"\n    "
		current_model = current_model.replace('EXTRA_TAGS', group_str)
		current_model = current_model.replace('# ', '')
		tf_config += "\n" + current_model

	return tf_config