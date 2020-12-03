import unittest
from os.path import join, expanduser
import pkg_resources
import sys
import io
import os
from yggdrasil.yggdrasil import run
from ..common_tools import create_logger

from yggdrasil.terraform.terraform_init import prepare_ssh_keys

DATA_PATH = pkg_resources.resource_filename('yggdrasil', '.')
TEST_PATH = pkg_resources.resource_filename('yggdrasil', '..', 'test')

class GlobalTest(unittest.TestCase) :

	""" Test case for first function """

	""" prepare setup """
	def setUp(self) :
		self.name = 'test'
		self.logger = create_logger(os.path.join(TEST_PATH, '.'))
		self.workfolder = TEST_PATH
		self.scope = "test_scope"
		self.provider = "test_provider"
		self.secrets_folder = os.path.join(TEST_PATH, "secrets", self.scope)
		self.ssh_private_folder = os.path.join(TEST_PATH, "secrets", "ssh", "private")
		self.ssh_public_folder = os.path.join(TEST_PATH, "secrets", "ssh", "public")
	
	""" tear down """
	def tearDown(self) :
		self.name = None

	""" test prepare_ssh_keys """
	def test_prepare_ssh_keys(self) :
		
		prepare_ssh_keys(self.logger, self.provider, self.scope, self.workfolder)

		ssh_keys = ["ssh_key"]
		for ssh_key in ssh_keys :
			self.assertTrue(os.path.exists(os.path.join(self.ssh_private_folder, ssh_key)))
			self.assertTrue(os.path.exists(os.path.join(self.ssh_public_folder, ssh_key)))


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