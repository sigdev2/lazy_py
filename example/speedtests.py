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

import timeit


def testVS(one, two, module, times=10):
    out = str(timeit.timeit(one + r'()',
                            setup=r'from ' + module + r' import ' + one,
                            number=times))
    out += r' vs '
    out += str(timeit.timeit(two + r'()',
                             setup=r'from ' + module + r' import ' + two,
                             number=times))
    print(out)


if __name__ == r'__main__':
    print(r' lazy_py  ||  itertools')
    print(r'----speed_groupby------')
    testVS(r'speed_groupby_liner', r'speed_groupby_liner_it', r'speed_groupby')
    testVS(r'speed_groupby_rec', r'speed_groupby_rec_it', r'speed_groupby')
    print(r'----speed_zip----------')
    testVS(r'speed_zip', r'speed_zip_it', r'speed_zip')
    print(r'----speed_takewhile----')
    testVS(r'speed_takewhile_n', r'speed_takewhile_n_it', r'speed_takewhile')
    testVS(r'speed_takewhile_f', r'speed_takewhile_f_it', r'speed_takewhile')
    print(r'----speed_repeat-------')
    testVS(r'speed_repeat', r'speed_repeat_it', r'speed_repeat')
    print(r'----speed_map-------')
    testVS(r'speed_map', r'speed_map_it', r'speed_map')
    print(r'----speed_filter-------')
    testVS(r'speed_filter', r'speed_filter_it', r'speed_filter')
    print(r'----speed_cycle-------')
    testVS(r'speed_cycle', r'speed_cycle_it', r'speed_cycle')
    print(r'----speed_chain-------')
    testVS(r'speed_chain', r'speed_chain_it', r'speed_chain')
