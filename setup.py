#!/usr/bin/env python

from distutils.core import setup

setup(name='pykstat',
      version='0.1',
      description='Native (ctypes) Solaris kstat Python binding and compatible utility',
      author='Cyril Plisko',
      author_email='cyril.plisko@mountall.com',
      maintainer='PyHedgehog',
      maintainer_email='pywebmail@list.ru',
      url='https://github.com/pyhedgehog/kstat',
      packages=['kstat'],
     )
