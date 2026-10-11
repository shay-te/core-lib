import os
import re

from setuptools import find_namespace_packages, find_packages, setup

dir_path = os.path.dirname(os.path.realpath(__file__))


# Everything is read as text: an isolated build has setuptools, but neither pip nor this library's dependencies.
def read_file(*path_parts) -> str:
    with open(os.path.join(dir_path, *path_parts), 'r') as file:
        return file.read()


version = re.search(
    r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", read_file('template_core_lib', '__init__.py'), re.M
).group(1)
install_requires = [
    line.split('#')[0].strip() for line in read_file('requirements.txt').splitlines() if line.split('#')[0].strip()
]

packages1 = find_packages(exclude=['tests', 'tests.*'])
packages2 = find_namespace_packages(include=['hydra_plugins.*'])
packages = list(set(packages1 + packages2))

setup(
    name='template_core_lib',
    version=version,
    author='template_full_name',
    author_email='template_email',
    description='template_description',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='template_url',
    packages=packages,
    license='template_license',
    # template_classifiers
    install_requires=install_requires,
    include_package_data=True,
    python_requires='>=3.10',
)
