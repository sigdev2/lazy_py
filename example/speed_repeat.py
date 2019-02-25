#!/usr/bin/env python
# -*- coding: utf-8 -*-

r''' Copyright 2018, SigDev

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License. '''

import itertools
from six.moves import xrange
from os.path import realpath
from os.path import dirname
import sys
sys.path.insert(0, realpath(dirname(realpath(__file__)) + r'/..'))
import lazy


def speed_repeat():
    out = []
    for n in lazy.Iterator(xrange(10)).repeat(2):
        out.append(n)

def speed_repeat_it():
    out = []
    for n in itertools.repeat(xrange(10), 2):
        out.append(n)


if __name__ == r'__main__':
    pass
