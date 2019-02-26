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
import lazy


# number
def speed_takewhile_n():
    text = r'abcdefg'
    out = []
    for ch in lazy.Iterator(text).takewhile(4):
        out.append(ch)


def speed_takewhile_n_it():
    # approximate algorithm
    text = r'abcdefg'
    out = []
    for ch in itertools.takewhile(lambda ch: ch != text[4], text):
        out.append(ch)


# func
def speed_takewhile_f():
    text = r'abcdefg'
    out = []
    for ch in lazy.Iterator(text).takewhile(lambda ch: ch != r'f'):
        out.append(ch)


def speed_takewhile_f_it():
    text = r'abcdefg'
    out = []
    for ch in itertools.takewhile(lambda ch: ch != r'f', text):
        out.append(ch)


if __name__ == r'__main__':
    pass
