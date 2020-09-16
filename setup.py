from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='yggdrasil',
	  version='0.1',
	  description='A python package to create data intelligence workflow',
	  url='https://github.com/adeblonde/yggdrasil_v2',
	  author='Antoine Deblonde',
	  author_email='antoine.deblonde@protonmail.ch',
	  license='LGPLv3',
	  packages=['yggdrasil'],
	  install_requires=[
		  'Click',
		  'python-terraform',
		  'pyyaml'
	  ],
	  entry_points={
		'console_scripts': 
		[
			'ygg=yggdrasil.yggdrasil:ygg',
			'ygg-config=yggdrasil.yggdrasil:ygg_config'
		]
	  },
	  test_suite='nose.collector',
	  tests_require=['nose'],
	  include_package_data=True,
	  zip_safe=False)