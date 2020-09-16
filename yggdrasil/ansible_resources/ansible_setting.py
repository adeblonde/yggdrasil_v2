import json
import os
from os.path import join
from yggdrasil.common_tools import makedir_p
import shutil
import subprocess
from multiprocessing import Process, Queue, current_process
import time
import queue # imported for using queue.Empty exception
from yggdrasil.common_tools import load_aws_credentials

def ansible_set_aws(logger, work_dir, config):

	""" this function creates an encrypted YAML file for storing AWS credentials for further use by Ansible """
	cloud_creds = load_aws_credentials(logger, config['infrastructure']['credentials_file'])

	

def gather_ips(work_dir, ami2user, logger) :

	""" this function parse a Terraform .tfstate in order to gather the public IPs of its virtual hosts """

	host_ips = dict()
	host_usernames = dict()
	group_hosts = dict()

	tf_state_file = join(work_dir, 'terraform.tfstate')
	if os.path.isfile(tf_state_file) :
		with open(tf_state_file, 'r') as f :
			tfstate = json.load(f)
			modules = tfstate['modules']
			for module in modules :
				if 'resources' in module.keys() :
					resources = module['resources']
					for elt in resources.keys() :
						sub_elts = elt.split('.')
						# """ if it is an AWS instance, let's parse it """"
						if sub_elts[0] == 'aws_instance' :
							ip_address = resources[elt]['primary']['attributes']['public_ip']
							host_username = ami2user[resources[elt]['primary']['attributes']['ami']]
							host_name = 'dummy_name'
							for attr in resources[elt]['primary']['attributes'] :
								if attr == 'tags.Name' :
									host_name = resources[elt]['primary']['attributes'][attr]
									break
							for attr in resources[elt]['primary']['attributes'] :
								if attr[:11] == 'tags.Group_' :
									group_name = attr[11:]
									if group_name not in group_hosts.keys() :
										group_hosts[group_name] = [host_name]
									else :
										group_hosts[group_name].append(host_name)
									logger.info("Adding host %s to group %s" % (host_name, group_name))
							logger.info("Adding IP %s to host %s" % (ip_address, host_name))
							host_ips[host_name] = ip_address
							host_usernames[host_name] = host_username

	return host_ips, host_usernames, group_hosts

def create_config_tree(logger, work_dir):

	""" this function create an Ansible configuration folder tree, as described in Ansible's best practices """

	ansible_dir = join(work_dir, 'ansible')
	makedir_p(ansible_dir)
	ansible_production_dir = join(ansible_dir, 'production')
	makedir_p(ansible_production_dir)
	ansible_roles_dir = join(ansible_dir, 'roles')
	makedir_p(ansible_roles_dir)

	return ansible_dir, ansible_production_dir, ansible_roles_dir

def create_host_file(logger, config, host_ips, host_usernames, group_hosts, ansible_production_dir) :

	""" this function generates an host file for Ansible configuration, with all the hosts referenced by providers """

	ansible_host_str = ""

	""" all hosts """
	ansible_host_str += "[" + config['config_name'] + "]"
	for host in host_ips.keys() :
		ansible_host_str += '\nid_' + host + '	ansible_ssh_host=' + host_ips[host] + '	ansible_ssh_user='+ host_usernames[host]

	""" hosts groups """
	for group in group_hosts.keys() :
		ansible_host_str += "\n\n"
		ansible_host_str += "[" + group + "]"
		# ansible_host_str += "[" + config['config_name'] + "_" + group + "]"
		for host in group_hosts[group]:
			ansible_host_str += '\nid_' + host + '	ansible_ssh_host=' + host_ips[host] + '	ansible_ssh_user='+ host_usernames[host]
		# with open(join(work_dir, config['config_name'] + '_' + group + '.ini'), 'w') as f:
			# f.write(ansible_host_str)
		
	""" every host """
	for host in host_ips.keys() :
		ansible_host_str += "\n\n"
		ansible_host_str += "[" + host + "]"
		# ansible_host_str += "[" + config['config_name'] + "_" + host + "]"
		ansible_host_str += '\nid_' + host + '	ansible_ssh_host=' + host_ips[host] + '	ansible_ssh_user='+ host_usernames[host]
		# with open(join(work_dir, config['config_name'] + '_' + host + '.ini'), 'w') as f:
			# f.write(ansible_host_str)

	production_hosts_path = join(ansible_production_dir, config['config_name'] + '.hosts')
	with open(production_hosts_path, 'w') as f:
		f.write(ansible_host_str)

	return production_hosts_path

def collect_playbooks_paths(logger, config, playbooks_folder):

	""" this function gathers all the playbooks paths into a dictionary playbook <-> absolute path """
	playbooks_path = dict()

	if 'extra_job_folders' in config.keys() :
		for extra_folder in config['extra_job_folders'] :
			playbooks_folder.append(extra_folder)
		
	for folder in playbooks_folder :
		if os.path.exists(folder) :
			for playbook in os.listdir(folder) :
				if playbook.split('.')[-1] in ['yml', 'yaml']:
					# playbook_name = os.path.basename(playbook).split('.')[0]
					if playbook not in playbooks_path.keys() :
						playbooks_path[playbook] = join(folder, playbook)
			else :
				logger.info("Warning : %s is not a folder" % folder)

	logger.info("All playbooks paths : %s" % playbooks_path)
	return playbooks_path

def collect_synchronous_jobs(logger, config, ansible_roles_dir, ansible_dir, playbooks_path, ansible_cloud_creds) :

	""" this function parse the config file from Yggdrasil, and create Ansible playbooks inside Ansible config tree, 
	in order to execute all synchronous jobs defined in the config file """

	main_yaml = "---"

	for job in config['sync_jobs']['job_list'] :
		job = job['job']
		main_yaml += "\n- import_playbook: " + job['name'] + '.yml'
		job_yaml = "---\n- hosts : "
		for target in job['target']:
			job_yaml += target + " :"
		if job_yaml[-1] == ':' :
			job_yaml = job_yaml[:-1]
		job_yaml += "\n  gather_facts : no"
		job_yaml += "\n  roles :"
		for script in job['scripts']:
			if script in playbooks_path.keys() :
				role_name = os.path.basename(script).split('.')[0]
				job_yaml += "\n    - " + role_name

				""" for each 'script' that will be executed, we create an associated ansible role """
				ansible_role_dir = join(ansible_roles_dir, role_name)
				makedir_p(ansible_role_dir)
				ansible_tasks_dir = join(ansible_role_dir, 'tasks')
				makedir_p(ansible_tasks_dir)
				shutil.copyfile(playbooks_path[script], join(ansible_tasks_dir, 'main.yml'))
				ansible_vars_dir = join(ansible_role_dir, 'vars')
				makedir_p(ansible_vars_dir)
				shutil.copyfile(ansible_cloud_creds, join(ansible_vars_dir, 'cloud_creds.yml'))
			else :
				logger.info("Warning : playbook %s not referenced" % script)

		""" creating job yaml file, that will execute roles associated with this job """
		job_ansible_path = join(ansible_dir, job['name'] + '.yml')
		with open(job_ansible_path, 'w') as f :
			f.write(job_yaml)

	main_ansible_file = config['config_name'] + '.yml'
	main_ansible_path = join(ansible_dir, main_ansible_file)
	logger.info("Creating main ansible file : %s" % main_ansible_path)
	with open(main_ansible_path, 'w') as f :
		f.write(main_yaml)

	return main_ansible_path


def prepare_pool_jobs(logger, config, ansible_dir, production_hosts_path, playbooks_path, group_hosts, ansible_cloud_creds) :

	""" this function parse the config file to prepare Ansible playbooks for all pool jobs """

	def pool_job(job_queue, done_queue, host):

		""" target function for pool jobs process """
		while True :
			try :
				task = job_queue.get_nowait()
				try :
					result = subprocess.call(['/usr/bin/ansible-playbook', '-i', production_hosts_path, join(ansible_dir, 'pool', task), 
					'--limit', host,
					'--vault-password-file', config['ansible_resources']['vault_password_file'],
					'--key-file', config['infrastructure']['private_ssh_key_path']],
					env={'ANSIBLE_HOST_KEY_CHECKING':'False'})
					logger.info("Result of ansible call : %s" % result)
				except :
					logger.info("Problem in the execution of ansible playbooks")
			except queue.Empty :
				break
			else :
				done_queue.put(task + ' done by process ' + str(current_process()))
				time.sleep(0.5)
		return True

	jobs_queues = dict()
	done_queues = dict()
	processes = []
	if 'pool_jobs' in config.keys() :
		ansible_pool_dir = join(ansible_dir, 'pool')
		makedir_p(ansible_pool_dir)
		# shutil.copyfile(ansible_cloud_creds, os.path.join(ansible_pool_dir, os.path.basename(ansible_cloud_creds)))
		playbook_input = ''
		ansible_cloud_creds_basename = os.path.basename(ansible_cloud_creds)

		for job in config['pool_jobs']['job_list'] :
			job = job['job']
			jobs_queues[job['name']] = Queue()
			done_queues[job['name']] = Queue()
			for script in job['scripts'] :
				jobs_queues[job['name']].put(script)
				""" copying playbook for pool job while setting the cloud creds file """
				with open(playbooks_path[script], 'r') as f :
					playbook_input = f.read()
				playbook_input = playbook_input.replace('ANSIBLE_CLOUD_CREDS', ansible_cloud_creds_basename)
				logger.info("Creating pool job playbook %s" % join(ansible_pool_dir, script))
				with open(join(ansible_pool_dir, script), 'w') as f :
					f.write(playbook_input)
				# shutil.copyfile(playbooks_path[script], join(ansible_pool_dir, script))
			for target in job['target'] :
				if target in group_hosts.keys() :
					for host in group_hosts[target] :
						p = Process(target = pool_job, args=(jobs_queues[job['name']], done_queues[job['name']], host))
						processes.append(p)
				else :
					p = Process(target = pool_job, args=(jobs_queues[job['name']], done_queues[job['name']], target))
					processes.append(p)

	return processes