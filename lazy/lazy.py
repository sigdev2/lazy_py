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
# lazy iterator for buffering - return not calculated buffer when scan or
#     group element, and calculate buffer len only when get next element
# use Coverage for tests
# use Tox for test compatibility
# perfomance compare with iterator tools


class Command:
    def __init__(self, f, done_exit=True):
        if done_exit:
            self.op = lambda val, done, buffer, it: \
                ((None, None) if done else f(val, done, buffer, it))
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

    def clear(self, obj=None, parent=None):
        self.value = obj
        self.parent = parent
        return self.value


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
                        item = None
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
                    val, stat = self.__commands[i].op(item, done, buffer, self)
                    if not done:
                        if stat is False or stat == r's':  # skip
                            is_skip = True
                            break
                        elif stat == r'r':  # repeat
                            continue
                    if stat is True or stat == r'n':  # don't change
                        pass
                    elif stat is None or stat == r'd':  # done
                        raise StopIteration
                    elif stat == list or stat == r'l':  # list
                        if not done and len(buffer) > 0:
                            buffer.pop()
                        it = IteratorsTree(iter(val))
                        it.i = i + 1
                        it.parent = self.__it
                        self.__it = it
                        # note: clear buffer is operation duty
                        is_skip = True
                    else:  # value
                        item = val
                        if done or len(buffer) == 0:
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
            if isinstance(value, list):
                return val, val not in value
            return val, val != value
        self.__commands.append(Command(removeLambda))
        return self

    def groupby(self, f=lambda v, b, s: v, recursive=True, swither_inc=False):
        d = []
        nl = {r's': [None], r'd': d, r'c': TreePtr(d),
              r'i': swither_inc, r'r': recursive}

        def groupLambda(val, done, buf, it):
            newstate = None
            rec = nl[r'r']
            st = nl[r's']
            si = nl[r'i']
            root = nl[r'd']
            cur = nl[r'c']
            last = st[-1]
            if done:
                if len(buf) == 0:
                    if len(root) > 0:
                        del st[1:]
                        ret = root
                        nl[r'd'] = cur.clear([])
                        return ret, list
                    return None, None
            else:
                newstate = f(val, buf, last)
            buflen = len(buf)

            if newstate is False:
                newstate = None
            if newstate == NotImplemented:
                newstate = st[-2] if last is not None else None
            if last == newstate:  # state not changed
                if newstate is None:
                    return buf.pop(), NotImplemented
                return None, False  # skip
            # change state
            for _ in xrange(buflen - 1):
                cur.value.append(buf.pop(0))
            if newstate is None:  # state -> None
                if done or si:
                    cur.value.append(buf.pop())
                del st[1:]
                ret = root
                nl[r'd'] = cur.clear([])
                if len(buf) > 0:
                    ret.append(buf.pop())
                return ret, list
            else:  # state -> state or  # None -> state
                mode = rec  # liner
                if rec:
                    if last is not None and st[-2] == newstate:  # up
                        st.pop()
                    else:  # down
                        st.append(newstate)
                        mode = None
                else:  # liner
                    if last is None:
                        st.append(newstate)
                    else:
                        st[-1] = newstate

                si = si and mode
                if si:
                    cur.value.append(val)
                if mode:  # up
                    nl[r'c'] = cur.parent
                else:  # down or liner
                    if mode is None or last is None:
                        nl[r'c'] = TreePtr([], cur)
                    else:
                        nl[r'c'] = TreePtr([], cur.parent)
                    nl[r'c'].parent.value.append(nl[r'c'].value)
                if not si:
                    nl[r'c'].value.append(val)
            buf.pop()
            return None, False  # skip

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
