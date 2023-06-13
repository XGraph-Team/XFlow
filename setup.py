#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='xflow-net',
    version='0.0.1',
    author='xgraphing',
    author_email='zchen@cse.msstate.edu',
    url='https://xflow.network/',
    description='a python library for graph flow',
    packages=['xflow-net'],
    install_requires=['networkx', 'ndlib'],
    entry_points={
        'console_scripts': [
            'xflow=xflow-net:xflow',
        ]
    }
)
