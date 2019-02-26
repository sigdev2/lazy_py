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


def speed_cycle():
    arr = [1, 2, 3, 4, 5]
    out = []

    n = 0
    for ch in lazy.Iterator(arr).cycle():
        out.append(ch)
        n += 1
        if n >= 5:
            break


def speed_cycle_it():
    arr = [1, 2, 3, 4, 5]
    out = []

    n = 0
    for ch in itertools.cycle(arr):
        out.append(ch)
        n += 1
        if n >= 5:
            break


if __name__ == r'__main__':
    pass
