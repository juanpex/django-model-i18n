#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
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

def fullsplit(path, result=None):
    """
Split a pathname into components (the opposite of os.path.join)
in a platform-neutral way.
"""
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'model_i18n'

for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames:
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


setup(name='django-model-i18n',
      version=version,
      author='juanpex',
      author_email='jpma55@gmail.com',
      description='django-model-i18n is a django application that tries to make multilingual data in models less painful.',
      download_url='https://github.com/juanpex/django-model-i18n/zipball/master/',
      license='BSD',
      keywords='django, model, i18n, translation, translations, python, pluggable',
      url='https://github.com/juanpex/django-model-i18n',
      packages=packages,
      package_data=package_data,
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
