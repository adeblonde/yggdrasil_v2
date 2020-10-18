import unittest
from os.path import join, expanduser
import pkg_resources
import sys
import io
from yggdrasil.yggdrasil import run

DATA_PATH = pkg_resources.resource_filename('yggdrasil', '.')

class GlobalTest(unittest.TestCase) :

	""" Test case for first function """

	""" prepare setup """
	def setUp(self) :
		self.name = 'test'
	
	""" tear down """
	def tearDown(self) :
		self.name = None

	""" test writing to S3 """
	def test_write2s3(self) :
		self.name = 'test writing to S3'

	""" test running a config file """
	def test_run(self) :

		""" define config file and parameters file """
		CONFIG_FILE = join(DATA_PATH, 'test', 'test_config.yml')
		PARAMS_FILE = join(expanduser('~'), 'workspace', 'work', 'yggdrasil_test_parameters.yml')
		WORK_FOLDER = join(expanduser('~'), 'workspace', 'work', 'test_config')

		""" redirect print to stdout """
		stdout_str = io.StringIO()
		sys.stdout = stdout_str

		run(CONFIG_FILE, WORK_FOLDER, PARAMS_FILE)

		""" print debug information """
		sys.stdout = sys.__stdout__
		print("Debug print \n", stdout_str.getvalue())
	

if __name__ == '__main__':
	unittest.main()