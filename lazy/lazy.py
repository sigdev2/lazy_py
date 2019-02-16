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

from six.moves import xrange, reduce
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from collections import deque
import copy

from .utils import TreePtr, Ptr
from .cache import cached as cache_cached

# todo
# Refactoring iterator, tree iterator, GrammarContext
# Refactoring sublist to return tem falue True or False
# Refactoring tokenize functions to remove comments, split space tokens,
#     brekets recursion, screened items, regexps
# itertools functions
# cached calculations
# paralel calculatons for variatic tokenizrer and chooses in grammar
# ReadDocs documentation
# speed tests
# use Coverage for tests
# use Tox for test compatibility
# perfomance compare with iterator tools


class Command:
    __slots__ = [r'op', r'id', r'__hash']

    def __init__(self, cid, f, done_exit=True,
                 cached=True, cache_items=128,
                 cache_min=304, cache_max=3072,
                 hash_add=None):
        self.id = cid
        out = f
        if done_exit:
            def endIfDone(val, done, buffer, it):
                return ((None, None) if done else f(val, done, buffer, it))
            out = endIfDone

        if cached:
            @cache_cached(cache_items, cache_min, cache_max, hash_add)
            def cachedOp(val, done, buffer, it):
                return out(val, done, buffer, it)
            self.op = cachedOp
            self.__hash = hash(self.id)
        else:
            self.op = out

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.__hash


class Iterator:
    __slots__ = [r'__obj', r'__parent',
                 r'__commands',
                 r'__cached', r'__cache_items',
                 r'__cache_min', r'__cache_max',
                 r'__static_hash',
                 r'__command', r'__it',
                 r'__current', r'__idx',
                 r'__memo_hash']

    def __init__(self, obj, parent=None):
        if isinstance(obj, Iterable) or \
           hasattr(obj, r'__iter__ '):
            self.__obj = obj
        else:
            self.__obj = (obj)

        self.__parent = parent
        self.__commands = []

        # cache
        self.__cached = False
        self.__cache_items = 128
        self.__cache_min = 304
        self.__cache_max = 3072

        # hash
        self.__static_hash = str(id(obj)) + ('' if parent is None
                                             else str(id(parent)))

        # reset()
        self.__command = None
        self.__it = iter(self.__obj)
        self.__current = None
        self.__idx = -1
        self.__memo_hash = None

    def __iter__(self):
        return self

    def __copy__(self):
        return self.clone()

    def __deepcopy__(self, memo=None):
        return self.clone()

    def __next__(self):
        return self.next()

    def __eq__(self, other):
        return id(self.__obj) == id(other.__obj) and \
               self.__commands == other.__commands and \
               self.__idx == other.__idx

    def __hash__(self):
        if self.__memo_hash is None:
            self.__memo_hash = hash(self.__static_hash +
                                    str(self.__idx) +
                                    str(self.__command) +
                                    reduce(lambda x, y: x + y.id,
                                           self.__commands, r''))
        return self.__memo_hash

    def copy(self):
        return self.clone()

    def clone(self):
        it = Iterator(self.__obj, self.__parent)
        it.__commands = copy.deepcopy(self.__commands)
        it.__command = self.__command
        it.__current = self.__current

        it.__cached = self.__cached
        it.__cache_items = self.__cache_items
        it.__cache_min = self.__cache_min
        it.__cache_max = self.__cache_max

        it.__idx = self.__idx

        source = self.__it
        own = deque()
        ex = deque()

        def gen(mydeque):
            while True:
                if not mydeque:             # when the local deque is empty
                    newval = next(source)   # fetch a new value and
                    own.append(newval)      # load it to all the deques
                    ex.append(newval)
                yield mydeque.popleft()
        self.__it = gen(own)
        it.__it = gen(ex)
        return it

    def next(self):
        item = None
        done = True
        buffer = []
        while True:
            while True:
                try:
                    item = next(self.__it)
                    done = False
                    break
                except StopIteration:
                    done = True
                    if hasattr(self.__it, r'_Iterator__parent') and \
                       self.__it.__parent is not None:
                        self.__it = self.__it.__parent
                    else:
                        item = None
                        break

            if done:
                if len(self.__commands) == 0:
                    raise StopIteration
            else:
                buffer.append(item)
            is_skip = False
            start = self.__command
            if hasattr(self.__it, r'_Iterator__command'):
                start = self.__it.__command
            for i in xrange(len(self.__commands)):
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
                        it = Iterator(val, self.__it)
                        it.__command = i + 1
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
        self.__memo_hash = None
        return item

    def reset(self):
        self.__command = None
        self.__it = iter(self.__obj)
        self.__current = None
        self.__idx = -1
        self.__memo_hash = None

    def clean(self):
        self.__commands = []
        self.__cached = False
        self.reset()

    def cache(self, c=True, cache_items=128,
              cache_min=304, cache_max=3072,):
        self.__cached = c
        self.__cache_items = cache_items
        self.__cache_min = cache_min
        self.__cache_max = cache_max
        return self

    def nocache(self, nc=True):
        self.__cached = not nc
        return self

    def add_command(self, cid, f, done_exit=True, cached=None):
        self.__memo_hash = None
        self.__commands.append(Command(cid, f,
                                       done_exit,
                                       self.__cached if cached is None
                                       else bool(cached),
                                       self.__cache_items,
                                       self.__cache_min,
                                       self.__cache_max))
        return self

    def map(self, f):
        def inner(val, done, buffer, it):
            return f(val), NotImplemented
        return self.add_command(r'map', inner)

    def filter(self, f):
        def inner(val, done, buffer, it):
            return val, bool(f(val))
        return self.add_command(r'filter', inner)

    def remove(self, value):
        def inner(val, done, buffer, it):
            if isinstance(value, list):
                return val, val not in value
            return val, val != value
        return self.add_command(r'remove', inner)

    def groupby(self, f=lambda v, b, s: v, recursive=True, swither_inc=False):
        root = Ptr([])
        st = Ptr([None])
        cur = Ptr(TreePtr(root.p))

        def inner(val, done, buf, it):
            newstate = None
            last = st.p[-1]
            if done:
                if len(buf) == 0:
                    if len(root.p) > 0:
                        del st.p[1:]
                        ret = root.p
                        root.p = cur.p.clear([])
                        return ret, list
                    return None, None
            else:
                newstate = f(val, buf, last)
            buflen = len(buf)

            if newstate is False:
                newstate = None
            if newstate == NotImplemented:
                newstate = st.p[-2] if last is not None else None
            if last == newstate:  # state not changed
                if newstate is None:
                    return buf.pop(), NotImplemented
                return None, False  # skip
            # change state
            for _ in xrange(buflen - 1):
                cur.p.p.append(buf.pop(0))
            if newstate is None:  # state -> None
                if done or swither_inc:
                    cur.p.p.append(buf.pop())
                del st.p[1:]
                ret = root.p
                root.p = cur.p.clear([])
                if len(buf) > 0:
                    ret.append(buf.pop())
                return ret, list
            else:  # state -> state or  # None -> state
                mode = recursive  # liner
                if recursive:
                    if last is not None and st.p[-2] == newstate:  # up
                        st.p.pop()
                    else:  # down
                        st.p.append(newstate)
                        mode = None
                else:  # liner
                    if last is None:
                        st.p.append(newstate)
                    else:
                        st.p[-1] = newstate

                local_si = swither_inc and mode
                if local_si:
                    cur.p.p.append(val)
                if mode:  # up
                    cur.p = cur.p.parent
                else:  # down or liner
                    if mode is None or last is None:
                        cur.p = TreePtr([], cur.p)
                    else:
                        cur.p = TreePtr([], cur.p.parent)
                    cur.p.parent.p.append(cur.p.p)
                if not local_si:
                    cur.p.p.append(val)
            buf.pop()
            return None, False  # skip

        return self.add_command(r'groupby', inner, False, False)

    def scan(self, f):
        def inner(val, done, buffer, it):
            if done:
                return None, None
            ret = f(val)
            if isinstance(ret, Iterable):
                return ret, list
            return val
        return self.add_command(r'scan', inner)


if __name__ == r'__main__':
    pass
