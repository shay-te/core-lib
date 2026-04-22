import os

import core_lib

from setuptools import find_namespace_packages, setup, find_packages
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements

dir_path = os.path.dirname(os.path.realpath(__file__))
install_reqs = parse_requirements(os.path.join(dir_path, 'requirements.txt'), session=PipSession)

packages1 = find_packages()
packages2 = find_namespace_packages(include=['hydra_plugins.*'])
packages = list(set(packages1 + packages2))

with open('README.md', 'r') as fh:
    long_description = fh.read()

    setup(
        name='core-lib',
        version=core_lib.__version__,
        author='Shay Tessler',
        author_email='shay.te@gmail.com',
        description='basic onion architecture library utils',
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
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        install_requires=[
            'hydra-core==1.2', 'omegaconf', 'python-dateutil', 'PyJWT',
            'argh', 'pytimeparse', 'parsedatetime', 'click', 'requests', 'setuptools',
        ],
        extras_require={
            'sqlalchemy':    ['sqlalchemy==1.4.44', 'alembic', 'pymysql', 'psycopg2-binary', 'geoalchemy2', 'shapely'],
            'mongo':         ['pymongo'],
            'neo4j':         ['neo4j'],
            'redis':         ['redis'],
            'memcached':     ['python-memcached'],
            'solr':          ['pysolr'],
            'elasticsearch': ['elasticsearch'],
            'flask':         ['flask', 'flask_cors', 'flask_wtf'],
            'django':        ['django'],
            'aws':           ['boto3'],
            'crypto':        ['cryptography'],
            'all':           ['sqlalchemy==1.4.44', 'alembic', 'pymysql', 'psycopg2-binary', 'geoalchemy2', 'shapely',
                              'pymongo', 'neo4j', 'redis', 'python-memcached', 'pysolr', 'elasticsearch',
                              'flask', 'flask_cors', 'flask_wtf', 'django', 'boto3', 'cryptography'],
        },
        include_package_data=True,
        python_requires='>=3.7',
        scripts=['bin/core_lib'],
    )
