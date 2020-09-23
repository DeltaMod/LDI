# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:12:46 2020

@author: vidar
"""

import os
from setuptools import setup, find_packages, Command

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="LDI",
    version="0.0.1",
    packages=find_packages(),
    scripts=["LDI.py"],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["docutils>=0.3"],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
        # And include any *.msg files found in the "hello" package, too:
        "hello": ["*.msg"],
    },
    # metadata to display on PyPI
    author="Atli Vidar Már FLodgren",
    author_email="vidar.flodgren@sljus.lu.se",
    description="This is an Example Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="hello world example examples",
    url="https://github.com/DeltaMod/LDI",   # project home page, if any
    #project_urls={
    #    "Bug Tracker": "https://bugs.example.com/HelloWorld/",
    #    "Documentation": "https://docs.example.com/HelloWorld/",
    #    "Source Code": "https://code.example.com/HelloWorld/",
    #},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha"
    ]

    # could also include long_description, download_url, etc.
)
    
