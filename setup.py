import core_lib
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setuptools.setup(
   name='core-lib',
   version=core_lib.__version__,
   description='basic onion architecture libraray utils',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/shacoshe/core-lib.git",
   author='Shay Tessler',
   author_email='shay.te@gmail.com ',
   packages=setuptools.find_packages(),
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
   python_requires='>=3.7'
)