from setuptools import setup, find_packages

from codecs import open
from os import path

import sys

here = path.abspath(path.dirname(__file__))

# Python version-independent
install_requires = ['dateutil']

if sys.version_info < (3,4):
    install_requires = ['enum34']

# http://stackoverflow.com/a/26737672/877069
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='python-date-interval-generator',
    version='0.0.dev1',
    description='Generates common sequential date intervals for a given date range',
    # long_description=long_description, # TODO does this come 'magically'?
    author='@nutso',
    url='https://github.com/nutso/python-date-interval-generator',
    # TODO license
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='date interval dateutil',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    extras_require={
        'dev': [], # TODO
        'test': [], # TODO
    },
    test_suite="tests",
)
