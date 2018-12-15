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

import collections
from six.moves import xrange

# todo
# Refactoring iterator, tree iterator, GrammarContext
# Refactoring sublist to return tem falue True or False
# Refactoring tokenize functions to remove comments, split space tokens,
#     brekets recursion, screened items, regexps
# itertools functions
# xrange based on leazy iters
# cached calculations
# Optimize memory from freeze attributes for classes
# paralel calculatons for variatic tokenizrer and chooses in grammar
# read docs documentation
# speed tests


class Command:
    def __init__(self, f, done_exit=True):
        if done_exit:
            self.op = lambda val, done, buffer, it: ((None, None) if done else f(val, done, buffer, it))
        else:
            self.op = f


class IteratorsTree:
    def __init__(self, it):
        self.it = it
        self.parent = None
        self.i = None

    def __next__(self):
        return self.next()

    def next(self):
        return next(self.it)


class Ptr(object):
    def __init__(self, obj):
        self.value = obj


class TreePtr(Ptr):
    def __init__(self, obj, parent=None):
        super(TreePtr, self).__init__(obj)
        self.parent = parent


class Iterator:
    def __init__(self, obj):
        self.__obj = obj
        self.__commands = []
        self.__it = IteratorsTree(iter(self.__obj))
        self.__current = None
        self.__idx = -1

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        item = None
        done = True
        buffer = []
        while(True):
            while True:
                try:
                    item = next(self.__it)
                    done = False
                    break
                except StopIteration:
                    done = True
                    if self.__it.parent is not None:
                        self.__it = self.__it.parent
                    else:
                        break

            if not done:
                buffer.append(item)
            start = self.__it.i
            for i in xrange(len(self.__commands)):
                is_skip = False
                while True:
                    if start is not None:
                        i = start
                        start = None

                    if i >= len(self.__commands):
                        break
                    val, status = self.__commands[i].op(item, done, buffer, self)

                    if not status or status == r's':  # skip
                        is_skip = True
                    elif status or status == r'n':  # don't change
                        pass
                    elif status == r'r':  # repeat
                        continue
                    elif status is None or status == r'd':  # done
                        raise StopIteration
                    elif status == list or status == r'l':  # list
                        if len(buffer) > 0:
                            buffer.pop()
                        it = IteratorsTree(iter(val))
                        it.i = i + 1
                        it.parent = self.__it
                        self.__it = it
                        # note: clear buffer is operation duty
                        is_skip = True
                    else:  # value
                        item = val
                        if len(buffer) == 0:  # done == True is new item
                            buffer.append(item)
                        else:
                            buffer[-1] = item
                    break
                if is_skip:
                    break
            if is_skip:
                continue
            break

        self.__current = item
        self.__idx += 1
        return item

    def clean(self):
        self.__it = IteratorsTree(iter(self.__obj))
        self.__current = None
        self.__idx = -1

    def map(self, f):
        def mapLambda(val, done, buffer, it):
            return f(val), NotImplemented
        self.__commands.append(Command(mapLambda))
        return self

    def filter(self, f):
        def filterLambda(val, done, buffer, it):
            return val, bool(f(val))
        self.__commands.append(Command(filterLambda))
        return self

    def remove(self, value):
        def removeLambda(val, done, buffer, it):
            return val, val not in value if isinstance(value, list) else val != value
        self.__commands.append(Command(removeLambda))
        return self

    def groupby(self, f=lambda v, b: v):
        d = []
        nl = {r's': [None], r'd': d, r'c': TreePtr(d)}

        def groupLambda(val, done, buf, it):
            newstate = None
            if done:
                if len(buf) == 0:
                    return None, None
            else:
                newstate = f(val, buf)
            buflen = len(buf)

            last = nl[r's'][-1]
            if not newstate:
                newstate = None
            if last == newstate:
                return val, newstate is not None
            if newstate is not None:
                del nl[r's'][:]
                nl[r's'].append(None)
                for _ in xrange(buflen - 1):
                    nl[r'c'].value.append(buf.pop(0))
                if done:
                    nl[r'c'].value.append(buf.pop(0))
                ret = nl[r'd']
                nl[r'd'] = []
                nl[r'c'].value = nl[r'd']
                nl[r'c'].parent = None
                return [ret] + buf, list
            else:
                if len(nl[r's']) > 1 and nl[r's'][-2] == newstate:
                    nl[r's'].pop()
                    nl[r'c'] = nl[r'c'].parent
                else:
                    nl[r's'].append(newstate)
                    nl[r'd'] = []
                    nl[r'c'].value.append(nl[r'd'])
                    nl[r'c'] = TreePtr(nl[r'd'], nl[r'c'])

            for _ in xrange(buflen):
                nl[r'c'].value.append(buf.pop(0))

            if nl[r's'][-1] is not None:
                return None, False  # skip

            return nl[r'd'], NotImplemented

        self.__commands.append(Command(groupLambda, False))
        return self

    def scan(self, f):
        def scanLambda(val, done, buffer, it):
            if done:
                return None, None
            ret = f(val)
            if isinstance(ret, collections.Iterable):
                return ret, list
            return val

        self.__commands.append(Command(scanLambda))
        return self


if __name__ == r'__main__':
    pass
