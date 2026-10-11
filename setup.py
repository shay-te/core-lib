import os
import re

from setuptools import find_namespace_packages, setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))


# Everything is read as text: an isolated build has setuptools, but neither pip nor core_lib's dependencies.
def read_file(*path_parts) -> str:
    with open(os.path.join(dir_path, *path_parts), 'r') as file:
        return file.read()


version = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", read_file('core_lib', '__init__.py'), re.M).group(1)
install_requires = [
    line.split('#')[0].strip() for line in read_file('requirements.txt').splitlines() if line.split('#')[0].strip()
]

# Optional backends: install only the ones you use, e.g. pip install "core-lib[postgres,redis,flask]".
jwt_requires = ['PyJWT', 'cryptography']  # cryptography: JWTTokenHandler's ES* algorithms
extras_require = {
    'flask': ['flask'] + jwt_requires,  # HandleException also maps an expired JWT to a 401
    'django': ['django'] + jwt_requires,
    'jwt': jwt_requires,
    'postgres': ['psycopg2-binary'],
    'mysql': ['pymysql'],
    'mongodb': ['pymongo'],
    'solr': ['pysolr'],
    'neo4j': ['neo4j'],
    'redis': ['redis'],
    'memcached': ['python-memcached'],
    'elasticsearch': ['elasticsearch'],
    'geo': ['geoalchemy2', 'shapely'],
}
extras_require['all'] = sorted({requirement for requirements in extras_require.values() for requirement in requirements})
# Core-Lib's own test suite: [all] plus these.
extras_require['test'] = ['moto==5.2.3', 'boto3', 'freezegun', 'mongomock', 'flask_wtf', 'pandas']

packages1 = find_packages(exclude=['tests', 'tests.*', 'examples', 'examples.*'])
packages2 = find_namespace_packages(include=['hydra_plugins.*'])
packages = list(set(packages1 + packages2))

setup(
    name='core-lib',
    version=version,
    author='Shay Tessler',
    author_email='shay.te@gmail.com',
    description='Structure Python backends: wire services, data access and API clients once in a CoreLib object shared by web routes, jobs and tests.',
    long_description=read_file('README.md'),
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
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    python_requires='>=3.10',
    scripts=['bin/core_lib'],
)
