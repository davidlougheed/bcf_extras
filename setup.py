#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bcf_extras",
    version="0.2.0",

    python_requires="~=3.7",
    extras_require={
        "str": ["trtools"],
    },

    description="A set of variant file helper utilities built on top of bcftools and htslib.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/davidlougheed/bcf_extras",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
    ],

    author="David Lougheed",
    author_email="david.lougheed@gmail.com",

    packages=["bcf_extras"],
    include_package_data=True,

    entry_points={
        "console_scripts": ["bcf-extras=bcf_extras.entry:main"],
    },
)
