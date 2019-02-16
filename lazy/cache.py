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

__all__ = (r'get_size_rec', r'hashkey', r'cached')

from six import iteritems
try:  # Python 3
    from collections.abc import Hashable, Mapping
except ImportError:  # Python 2
    from collections import Hashable, Mapping
from sys import getsizeof
from numbers import Number


def get_size_rec(obj, seen=None, _zero_depth=None):
    if _zero_depth is None:
        try:  # Python 2
            _zero_depth = (basestring, Number, bytearray)
        except NameError:  # Python 3
            _zero_depth = (str, bytes, Number, bytearray)
    size = getsizeof(obj)
    if isinstance(obj, _zero_depth):
        return size

    if isinstance(obj, Mapping) or \
       hasattr(obj, r'__dict__') or \
       hasattr(obj, r'__iter__'):
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        if isinstance(obj, Mapping):
            size += sum([get_size_rec(k, seen, _zero_depth) +
                         get_size_rec(v, seen, _zero_depth)
                         for k, v in iteritems(obj)])
        elif hasattr(obj, r'__dict__'):
            size += get_size_rec(obj.__dict__, seen, _zero_depth)
        elif hasattr(obj, r'__iter__'):
            size += sum([get_size_rec(i, seen, _zero_depth) for i in obj])
    return size


def hashkey(*args, **kwargs):
    out = tuple(arg if isinstance(arg, Hashable)
                else id(arg)
                for arg in args)
    if kwargs:
        out = (out, tuple(arg if isinstance(arg, Hashable)
                          else (arg[0], id(arg[1]))
                          for arg in sorted(iteritems(kwargs))))
    return hash(out)


def cached(items=128, btmin=304, btmax=3072, add_to_hash=None):
    def newCache(f):
        cache = {}

        def inline(*args, **kwargs):
            key = hashkey(add_to_hash, *args, **kwargs)
            cl = len(cache)
            if cl > 1 and key in cache:
                val = cache[key]
                val[1] += 1
                return val[0]

            ret = f(*args, **kwargs)
            size = get_size_rec(ret)
            if size < btmin or size > btmax:
                return ret

            if cl > items:
                minKey = None
                minVal = None
                for k, v in iteritems(cache):
                    if minKey is None:
                        minKey = k
                        minVal = v[1]
                        continue
                    if minVal > v[1]:
                        minKey = k
                        minVal = v[1]
                del cache[minKey]

            cache[key] = [ret, 1]
            return ret
        return inline
    return newCache
