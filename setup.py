#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="crosswordist",
    version="0.0.1",
    author="karno-bh",
    author_email="karno.bh@gmail.com",
    description="Crosswordist application",
    license="MIT",
    keywords="crossword",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'crosswordist = karnobh.crosswordist.cli_app:main',
        ],
    },
    packages=find_packages()
)