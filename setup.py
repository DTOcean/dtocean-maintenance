# -*- coding: utf-8 -*-
"""This module contains the installation code of dtocean-maintenance

.. module:: setup.py
   :platform: Windows
   :synopsis: installation code of dtocean-maintenance
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

# pylint: disable=wrong-import-order

import os
import sys
from distutils.cmd import Command

import yaml
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
    
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class CleanPyc(Command):

    description = 'clean *.pyc'
    user_options = []
    exclude_list = ['.egg', '.git', '.idea', '__pycache__']
     
    def initialize_options(self):
        pass
     
    def finalize_options(self):
        pass
     
    def run(self):
        print "start cleanup pyc files."
        for pyc_path in self.pickup_pyc():
            print "remove pyc: {0}".format(pyc_path)
            os.remove(pyc_path)
        print "the end."
     
    def is_exclude(self, path):
        for item in CleanPyc.exclude_list:
            if path.find(item) != -1:
                return True
        return False
     
    def is_pyc(self, path):
        return path.endswith('.pyc')
     
    def pickup_pyc(self):
        for root, dirs, files in os.walk(os.getcwd()):
            for fname in files:
                if self.is_exclude(root):
                    continue
                if not self.is_pyc(fname):
                    continue
                yield os.path.join(root, fname)


def read_yaml(rel_path):
    with open(rel_path, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded


def get_appveyor_version():
    
    data = read_yaml("appveyor.yml")
    
    if "version" not in data:
        raise RuntimeError("Unable to find version string.")
    
    appveyor_version = data["version"]
    last_dot_idx = appveyor_version.rindex(".")
    
    return appveyor_version[:last_dot_idx]


setup(name='dtocean-maintenance',
      version=get_appveyor_version(),
      description='The maintenance operations module for the DTOcean tools',
      maintainer='Mathew Topper',
      maintainer_email='mathew.topper@dataonlygreater.com',
      license="GPLv3",
      packages=find_packages(),
      package_data={'dtocean_maintenance': ['config/*.yaml']
                    },
      setup_requires=['pyyaml'],
      install_requires=[
          'dtocean-economics >= 2.0, <3',
          'dtocean-logistics >= 3.0, <4',
          'dtocean-reliability >= 3.0, <4',
          'numpy',
          'pandas >=0.17',
          'polite >=0.9, <1',
          'setuptools'
      ],
      zip_safe=False, # Important for reading config files
      tests_require=['mock',
                     'pytest',
                     'pytest-mock'],
      cmdclass = {'test': PyTest,
                  'cleanpyc': CleanPyc,
                  },
      )
