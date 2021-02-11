import os

import setuptools

import core_lib

from setuptools import find_namespace_packages, setup
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements

dir_path = os.path.dirname(os.path.realpath(__file__))
install_reqs = parse_requirements(os.path.join(dir_path, 'requirements.txt'), session=PipSession)

packages1 = setuptools.find_packages()
packages2 = find_namespace_packages(include=['hydra_plugins.*'])
packages = list(set(packages1 + packages2))

with open('README.md', 'r') as fh:
   long_description = fh.read()

   setup(
      name='core-lib',
      version=core_lib.__version__,
      author='Your name',
      author_email='your@email.com',
      description='Your project description',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/shay-te/core-lib',
      packages=packages,
      license='MIT',
      classifiers=[
         'License :: OSI Approved :: MIT License',
         'Programming Language :: Python :: 3',
         'Operating System :: OS Independent',
         'Development Status :: 3 - Alpha',
         'Topic :: Software Development :: Libraries',
         'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      install_requires=[str(ir.requirement) for ir in install_reqs],
      include_package_data=True,
      python_requires='>=3.7',
      scripts=['bin/core_lib']
   )
