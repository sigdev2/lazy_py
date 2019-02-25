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
from os.path import realpath
from os.path import dirname
import sys
sys.path.insert(0, realpath(dirname(realpath(__file__)) + r'/..'))
import lazy


def speed_zip():
    one = [1, 2, 3, 4]
    two = [4, 3, 2, 1]
    out = []
    def totuple(*args):
        return (i for i in args)
    for o in lazy.Iterator(one).zip(totuple, two):
        out.append(o)


def speed_zip_it():
    one = [1, 2, 3, 4]
    two = [4, 3, 2, 1]
    out = []
    try:
        for o in itertools.izip(one, two):
            out.append(o)
    except:
        for o in itertools.zip_longest(one, two):
            out.append(o)


if __name__ == r'__main__':
    pass
