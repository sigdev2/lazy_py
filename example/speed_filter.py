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


def speed_filter():
    arr = [1, 2, 3, 4, 5]
    out = []

    for ch in lazy.Iterator(arr).filter(lambda x: x != 2):
        out.append(ch)


def speed_filter_it():
    arr = [1, 2, 3, 4, 5]
    out = []

    try:
        for ch in itertools.ifilter(arr, lambda x: x != 2):
            out.append(ch)
    except:
        for ch in itertools.filterfalse(lambda x: x != 2, arr):
            out.append(ch)


if __name__ == r'__main__':
    pass
