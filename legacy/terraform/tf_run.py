# import python_terraform as tf
from python_terraform import *

def run_terraform(logger, work_dir, config, tf_cloud_creds, dryrun) :

	""" this function executes Terraform actions according to a .tf file provided """
	tf = Terraform(working_dir=work_dir)
	if 'terraform_init' in config['infrastructure'].keys() :
		if config['infrastructure']['terraform_init'] == True :
			logger.info("Initializing")
			print(tf.init())
			logger.info("Terraform loaded")
	logger.info("Cloud credentials file used : %s" % tf_cloud_creds)

	if 'terraform_plan' in config['infrastructure'].keys() :
		if config['infrastructure']['terraform_plan'] == True:
			logger.info("Planning")
			print(tf.plan(no_color=IsFlagged, refresh=False, capture_output=True, var_file=tf_cloud_creds))

	if 'terraform_apply' in config['infrastructure'].keys() :
		if config['infrastructure']['terraform_apply'] == True :
			logger.info("Dryrun")
			dryrun = False
		else :
			dryrun = True
	if dryrun == False :
		logger.info("Applying")
		print(tf.apply(no_color=IsFlagged, refresh=False, skip_plan=True, var_file=tf_cloud_creds))

	if 'terraform_refresh' in config['infrastructure'].keys() :
		if config['infrastructure']['terraform_refresh'] == True :
			logger.info('Refreshing')
			print(tf.refresh(no_color=IsFlagged, var_file=tf_cloud_creds))

def destroy_terraform(logger, work_dir, tf_cloud_creds) :

	""" this function destroys Terraform infrastructure contained in .tfstate """
	tf = Terraform(working_dir=work_dir)
	logger.info("Refreshing before destruction")
	print(tf.refresh(no_color=IsFlagged, var_file=tf_cloud_creds))
	logger.info("Destroying")
	print(tf.destroy(no_color=IsFlagged, capture_output=True, var_file=tf_cloud_creds))