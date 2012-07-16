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
    url='https://github.com/gonz/django-model-i18n/',
    description="""django-model-i18n is a django application that tries to make multilingual data in models less painful.""",
    long_description=read(os.path.join(os.path.dirname(__file__), 'README.rst')),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
    ]
)
