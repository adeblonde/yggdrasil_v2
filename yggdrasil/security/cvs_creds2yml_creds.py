import os
import sys

def main() :

	""" create yaml file storing AWS creds from a csv file containing these credentials """
	if len(sys.argv) > 0 :
		input_file = sys.argv[1]
	else :
		input_file = 'aws_creds.csv'
	if os.path.exists(input_file) is not True :
		raise ValueError('The input file does not exist')

	if len(sys.argv) > 1 :
		output_file = sys.argv[2]
	else :
		output_file = 'aws_creds_encrypted.yml'

	aws_creds = dict()
	data = ['User name','Password','Access key ID','Secret access key','Console login link']
	
	with open(input_file, 'r') as f_read :
		data = f_read.read().split('\n')[1].split(',')
		aws_creds['aws_access_key_id'] = data[2]
		aws_creds['aws_secret_key'] = data[3]

	with open(output_file,'w') as f_write :
		f_write.write('---\n')
		f_write.write('aws_access_key_id : %s \n' % aws_creds['aws_access_key_id'])
		f_write.write('aws_secret_key : %s \n' % aws_creds['aws_secret_key'])

if __name__ == "__main__" :
    main()