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

# todo
# Refactoring iterator, tree iterator, GrammarContext
# Refactoring sublist to return tem falue True or False
# Refactoring tokenize functions to remove comments, split space tokens, brekets recursion, screened items, regexps
# itertools functions
# xrange based on leazy iters
# cached calculations
# Optimize memory from freeze attributes for classes

class Command:
    def __init__(self, f):
        self.op = f

class Sublist(list):
    pass

class IteratorsTree:
    def __init__(self, it):
        self.it = it
        self.parent = None
        self.i = None
    def __next__(self):
        return self.next()
    def next(self):
        return next(self.it)

class IteratorEx:
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
    
    def __xrange(self, num):
        if not hasattr(__builtins__, r'xrange'):
            return range(num)
        return xrange(num)

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
                    if self.__it.parent != None:
                        self.__it = self.__it.parent
                    else:
                        break

            if done == False:
                buffer.append(item)
            start = self.__it.i
            for i in self.__xrange(len(self.__commands)):
                is_skip = False
                while True:
                    if start != None:
                        i = start
                        start = None

                    if i >= len(self.__commands):
                        break
                    ret = self.__commands[i].op(item, done, buffer, self)

                    if ret == False: # skip
                        is_skip = True
                    else:
                        if ret == True: # don't change
                            pass
                        elif ret == r'r': # repeat
                            continue
                        elif ret == r'd':
                            raise StopIteration
                        elif isinstance(ret, Sublist): # buffer, hasattr(ret, r'__iter__')
                            if len(buffer) > 0:
                                buffer.pop()
                            it = IteratorsTree(iter(ret))
                            it.i = i + 1
                            it.parent = self.__it
                            self.__it = it
                            # note: clear buffer is operation duty
                            is_skip = True
                        else: # value
                            item = ret
                            if len(buffer) <= 0:
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
            if done:
                return r'd'
            val = f(val)
            return val

        self.__commands.append(Command(mapLambda))
        return self

    def filter(self, f):
        def filterLambda(val, done, buffer, it):
            if done:
                return r'd'
            return f(val)
        self.__commands.append(Command(filterLambda))
        return self

    def remove(self, value):
        def removeLambda(val, done, buffer, it):
            if done:
                return r'd'
            if isinstance(value, list):
                return not val in value
            return val != value
        self.__commands.append(Command(removeLambda))
        return self

    def group(self, f, g):
        def groupLambda(val, done, buffer, it):
            if done:
                if len(buffer) > 0:
                    out = []
                    for i in self.__xrange(len(buffer)):
                        out.append(buffer.pop(0))
                    return g(out, done)
                return r'd'
            if f(val, buffer):
                return False # skip
            # buffer is full
            out = []
            for i in self.__xrange(len(buffer)):
                out.append(buffer.pop(0))
            return g(out, done)

        self.__commands.append(Command(groupLambda))
        return self

    def scan(self, f):
        def scanLambda(val, done, buffer, it):
            if done:
                return r'd'
            ret = f(val)
            if not isinstance(ret, list):
                return val
            return Sublist(ret)

        self.__commands.append(Command(scanLambda))
        return self

if __name__ == r'__main__':
    pass