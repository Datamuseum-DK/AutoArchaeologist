#!/usr/bin/env python

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='autoarchaeologist',
    version='0.1',
    description='Presentation of datamedia as browsable HTML files',
    long_description=readme(),
    classifiers=[],
    keywords='reverse-engineering retro-computing preservation',
    url='https://github.com/Datamuseum-DK/AutoArchaeologist',
    author='Poul-Henning Kamp',
    author_email='phk@FreeBSD.org',
    license='BSD',
    packages=['autoarchaeologist'],
    zip_safe=False
)
