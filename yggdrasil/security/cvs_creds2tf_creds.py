import os
import sys
from os.path import expanduser

template_creds_aws = """
access_key = \"ACCESS_KEY_HERE\"
secret_key = \"SECRET_KEY_HERE\"
region     = \"AWS_REGION\"
"""

def main() :

	""" create .tf file storing AWS creds from a csv file containing these credentials """
	if len(sys.argv) > 0 :
		input_file = sys.argv[1]
	else :
		input_file = 'aws_creds.csv'
	if os.path.exists(input_file) is not True :
		raise ValueError('The input file does not exist')

	if len(sys.argv) > 2 :
		output_file = sys.argv[2]
	else :
		output_file = expanduser('~') + '/.terraform/aws_creds_terraform.tfvars'

	if len(sys.argv) > 3 :
		aws_region = sys.argv[3]
	else :
		aws_region = 'eu-west-1'

	aws_creds = dict()
	data = ['User name','Password','Access key ID','Secret access key','Console login link']
	
	with open(input_file, 'r') as f_read :
		data = f_read.read().split('\n')[1].split(',')
		aws_creds['aws_access_key_id'] = data[2]
		aws_creds['aws_secret_key'] = data[3]

	aws_creds_str = template_creds_aws.replace('ACCESS_KEY_HERE', aws_creds['aws_access_key_id'])
	aws_creds_str = aws_creds_str.replace('SECRET_KEY_HERE', aws_creds['aws_secret_key'])
	aws_creds_str = aws_creds_str.replace('AWS_REGION', aws_region)

	with open(output_file,'w') as f_write :
		f_write.write(aws_creds_str)

if __name__ == "__main__" :
    main()