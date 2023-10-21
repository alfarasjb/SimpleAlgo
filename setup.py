from setuptools import setup, find_packages

with open('README.md', 'r') as f:
	readme = f.read()


setup(
	name = 'PyAlgo',
	description = 'An algorithmic trading framework for MetaTrader5',
	long_description = readme,
	long_description_content_type = 'text/markdown',
	version = '0.0.1',
	author = 'Jay Alfaras',
	author_email = 'alfarasjb@gmail.com',
	url = '',
	packages = find_packages(),
	include_package_data = True
	)