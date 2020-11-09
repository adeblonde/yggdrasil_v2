import sys
import os
import logging
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import shutil

def find_exec_path(logger, executable) :

	""" this function returns the path to the Terraform executable """
	exec_path = shutil.which(executable)

	return exec_path

def load_aws_credentials(logger, aws_creds_file) :

	""" this function loads the AWS credentials from a file into a dictionary """

	aws_creds = dict()

	try :
		with open(aws_creds_file, 'r') as f_read :
			data = f_read.read().split('\n')[1].split(',')
			aws_creds['aws_access_key_id'] = data[2]
			aws_creds['aws_secret_key'] = data[3]
			print(aws_creds)
	except Exception as e :
		logger.info('The input file does not exist or cannot be read : error %s' % e)

	return aws_creds

def create_logger(logfile='') :

	""" this function create a nice logger object """

	if logfile == '' :
		logfile = os.getcwd()
		logfile = os.path.join(logfile,'yggdrasil.log')

	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	# create a file handler
	handler = logging.FileHandler(logfile)
	handler.setLevel(logging.INFO)

	# create a console handler
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.INFO)

	# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(handler)
	logger.addHandler(stdout_handler)

	logger.info('Logger created')

	return logger

def makedir_p(dir):

	""" simple function to create folder tree structure if not existing """
	
	if os.path.exists(dir) is False :
		os.makedirs(dir)

def set_ssh_connection() :

	""" this function set an SSH connection that will auto-accept unknown hosts """
	ssh = SSHClient()
	# ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(AutoAddPolicy())

	return ssh

def scp_data(ssh, logger, host_ips, group_hosts, host_usernames, config, mode='sending') :

	""" scp data to machines """
	for file_group in config['data_sending']:
		file_group = file_group['data']
		""" sending data by host name """
		logger.info("Sending data by host name")

		if 'by_names' in file_group.keys() :
			for host_name in file_group['by_names'] :
				try :
					logger.info("Connecting to host %s with user %s and key %s" % (host_ips[host_name], host_usernames[host_name], config['infrastructure']['private_ssh_key_path']))
					ssh.connect(host_ips[host_name], username=host_usernames[host_name], key_filename=config['infrastructure']['private_ssh_key_path'])
					logger.info("Connection set sucessfully")
					with SCPClient(ssh.get_transport()) as scp :
						if mode == 'sending' :
							scp.put(file_group['origin'], file_group['destination'])
						if mode == 'receiving' :
							scp.get(file_group['origin'], file_group['destination'])
				except :
					logger.info("Problem with SSH connection to host %s" % host_name)

		""" sending data by host group """
		logger.info("Sending data by host group")

		if 'by_groups' in file_group.keys() :
			for group_name in file_group['by_groups'] :
				for host_name in group_hosts[group_name] :
					try :
						logger.info("Connecting to host %s with user %s and key %s" % (host_ips[host_name], host_usernames[host_name], config['infrastructure']['private_ssh_key_path']))
						ssh.connect(host_ips[host_name], username=host_usernames[host_name], key_filename=config['infrastructure']['private_ssh_key_path'])
						logger.info("Connection set sucessfully")
						with SCPClient(ssh.get_transport()) as scp :
							if mode == 'sending' :
								scp.put(file_group['origin'], file_group['destination'])
							if mode == 'receiving' :
								scp.get(file_group['origin'], file_group['destination'])
					except :
						logger.info("Problem with SSH connection to host %s" % host_name)