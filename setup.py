#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Copyright 2018, SigDev

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License. '''

from setuptools import setup, find_packages
from os.path import join, dirname, realpath
import lazy

setup(name=lazy.__name__,
      version=lazy.__version__,
      packages=find_packages(exclude=['example']),
      description='Lazy calculations for Python',
      long_description=open(join(dirname(__file__), 'README.rst')).read(),
      author=lazy.__author__,
      license=lazy.__license__,
      url="http://github.com/sigdev2/lazy_py",
      keywords=' '.join([
        'python', 'lazy', 'parser', 'iterator', 'map', 'reduce', 'filter', 'parsing'
        ]
      ),
      classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Topic :: Software Development",
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'Topic :: Text Processing',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        ],
      install_requires=[],
      entry_points={},
      zip_safe=False
)
