# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in category_management/__init__.py
from category_management import __version__ as version

setup(
	name='category_management',
	version=version,
	description='Category Management',
	author='Gaisano',
	author_email='itdepartment.gaisano@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
