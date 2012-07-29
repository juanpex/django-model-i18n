#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages


read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()


setup(
    name="django-model-i18n",
    version="0.1",
    url='https://github.com/juanpex/django-model-i18n/',
    description="""django-model-i18n is a django application that tries to make multilingual data in models less painful.""",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
