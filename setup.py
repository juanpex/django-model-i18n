#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join, dirname
from setuptools import setup


version = __import__('model_i18n').__version__


LONG_DESCRIPTION = """
django-model-i18n
===================

django-model-i18n is a django application that tries to make multilingual data in models less painful.

    $ git clone git://github.com/juanpex/django-model-i18n.git
"""


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return LONG_DESCRIPTION


setup(name='django-model-i18n',
      version=version,
      author='juanpex',
      author_email='jpma55@gmail.com',
      description='django-model-i18n is a django application that tries to make multilingual data in models less painful.',
      download_url='https://github.com/juanpex/django-model-i18n/zipball/master/',
      license='BSD',
      keywords='django, model, i18n, translation, translations, python, pluggable',
      url='https://github.com/juanpex/django-model-i18n',
      packages=['model_i18n', ],
      package_data={'model_i18n': ['locale/*/LC_MESSAGES/*']},
      long_description=long_description(),
      install_requires=['django>=1.3', ],
      classifiers=['Framework :: Django',
                   'Development Status :: 3 - Alpha',
                   'Topic :: Internet',
                   'License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Environment :: Web Environment',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7'])
