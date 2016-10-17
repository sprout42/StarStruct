#!/usr/bin/env python

"""Setup script for StarStruct."""

import os
import setuptools

from starstruct import __project__, __version__

if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGES.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description="StarStruct allows for easy binary stream pack/unpack",
    url='https://github.com/sprout42/StarStruct',
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
        'Programming Language :: Python :: 3.5',
    ],

    install_requires=open('requirements.txt').readlines(),
)
