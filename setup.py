#!/usr/bin/env python

"""Setup script for NamedStruct."""

import setuptools

from namedstruct import __project__, __version__

import os
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGES.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description="NamedStruct is a Python 2 package.",
    url='https://github.com/sprout42/python-namedstruct',
    author='Aaron Cornelius',
    author_email='a.aaron.cornelius@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=open('requirements.txt').readlines(),
)
