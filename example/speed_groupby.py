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


# liner
def speed_groupby_liner():
    text = r'a{[()][(][)]}b'
    out = []

    def states(ch, b, s):
        if ch == r'(' or ch == r')':
            return r'c_bracket'
        if ch == r'{' or ch == r'}':
            return r's_bracket'
        if ch == r'[' or ch == r']':
            return r'k_bracket'
        return None
    for ch in lazy.Iterator(text).groupby(states, recursive=False):
        out.append(ch)


def speed_groupby_liner_it():
    text = r'a{[()][(][)]}b'
    out = []

    def states(ch):
        if ch == r'(' or ch == r')':
            return r'c_bracket'
        if ch == r'{' or ch == r'}':
            return r's_bracket'
        if ch == r'[' or ch == r']':
            return r'k_bracket'
        return None
    for ch in itertools.groupby(text, states):
        out.append(ch)


# recursive
def speed_groupby_rec():
    text = r'a{[()][(][)]}[]b'
    out = []

    def states(ch, b, s):
        if ch == r'(' or ch == r')':
            return r'c_bracket'
        if ch == r'{' or ch == r'}':
            return r's_bracket'
        if ch == r'[' or ch == r']':
            return r'k_bracket'
        return None

    for ch in lazy.Iterator(text).groupby(states):
        out.append(ch)


def speed_groupby_rec_it():
    text = r'a{[()][(][)]}[]b'

    # approximate algorithm
    def group_rec(obj):
        out = []
        state = [None]

        def states(ch):
            if ch == r'(' and state[0] != r'c_bracket':
                state[0] = r'c_bracket'
            if ch == r'{' and state[0] != r's_bracket':
                state[0] = r's_bracket'
            if ch == r'[' and state[0] != r'k_bracket':
                state[0] = r'k_bracket'

            if ch == r')' and state[0] == r'c_bracket':
                state[0] = None
                return r'c_bracket'
            if ch == r'}' and state[0] == r's_bracket':
                state[0] = None
                return r's_bracket'
            if ch == r']' and state[0] == r'k_bracket':
                state[0] = None
                return r'k_bracket'

            return state[0]

        for _, g in itertools.groupby(obj, states):
            items = list(g)
            if (items[0] == r'(' or
               items[0] == r'{' or
               items[0] == r'['):
                rec = [items[0]]
                rec.append(group_rec(items[1:-1]))
                rec.append(items[-1])
                out.append(rec)
            else:
                out.append(items)
        return out
    group_rec(text)


if __name__ == r'__main__':
    pass
