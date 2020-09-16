from yggdrasil.common_tools import load_aws_credentials, makedir_p
import os
import subprocess

template_creds_aws = """
access_key = \"ACCESS_KEY_HERE\"
secret_key = \"SECRET_KEY_HERE\"
region     = \"AWS_REGION\"
"""

def secure_ansible_aws(logger, auth_dir, aws_config, creds_file_path, vault_password_path) :

	""" this function creates an encrypted YAML file for storing AWS credentials
	for further use by Ansible """

	try :
		assert os.path.isfile(vault_password_path)
	except :
		logger.info("Vault password file does not exist")
		raise

	aws_creds = load_aws_credentials(logger, aws_config['credentials_file'])

	makedir_p(os.path.basename(creds_file_path))

	""" creating an unencrypted version of the yaml file """
	with open(creds_file_path,'w') as f_write :
		f_write.write('---\n')
		f_write.write('aws_access_key_id : %s \n' % aws_creds['aws_access_key_id'])
		f_write.write('aws_secret_key : %s \n' % aws_creds['aws_secret_key'])

	""" encrypting using ansible tools """
	try :
		result = subprocess.call([
			'/usr/bin/ansible-vault',
			'encrypt',
			creds_file_path,
			'--vault-password-file',
			vault_password_path
		])
		logger.info("Result of Ansible's encryption process %s" % result)
	except :
		logger.info("Problem in encryption process of yaml credentials file %s" % creds_file_path)
		os.remove(creds_file_path)
		raise

	logger.info("Encrypted AWS credentials for Ansible created at %s" % creds_file_path)
	
def secure_tf_aws(logger, auth_dir, aws_config, tf_aws_creds_file_path, aws_region='eu-west-1') :

	""" this function creates a separate Terraform .tfvars file in auth_dir to store AWS
	credentials securely """

	aws_creds = load_aws_credentials(logger, aws_config['credentials_file'])

	makedir_p(os.path.dirname(tf_aws_creds_file_path))

	aws_creds_str = template_creds_aws.replace('ACCESS_KEY_HERE', aws_creds['aws_access_key_id'])
	aws_creds_str = aws_creds_str.replace('SECRET_KEY_HERE', aws_creds['aws_secret_key'])
	aws_creds_str = aws_creds_str.replace('AWS_REGION', aws_region)

	with open(tf_aws_creds_file_path,'w') as f_write :
		f_write.write(aws_creds_str)
