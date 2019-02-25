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

from six import callable as six_callable, string_types
from six.moves import xrange, reduce
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from collections import deque
from numbers import Number
from math import factorial as fac
import copy

from .utils import TreePtr, Ptr
from .cache import cached as cache_cached

# todo
# Refactoring iterator, tree iterator, GrammarContext
# Refactoring sublist to return tem falue True or False
# Refactoring tokenize functions to remove comments, split space tokens,
#     brekets recursion, screened items, regexps
# itertools functions
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

    def __init__(self, obj=None, parent=None):
        self.__obj = obj
        self.__parent = parent
        self.__commands = []

        # cache
        self.__cached = False
        self.__cache_items = 128
        self.__cache_min = 304
        self.__cache_max = 3072

        # hash
        self.__static_hash = (self.obj_strid() +
                              (r'' if self.__parent is None
                               else str(id(self.__parent))))

        # reset()
        self.__command = None
        self.__it = self.obj_iter()
        self.__current = None
        self.__idx = -1
        self.__memo_hash = None

    # magics

    def __iter__(self):
        return self

    def __copy__(self):
        return self.clone()

    def __deepcopy__(self, memo=None):
        return self.clone()

    def __next__(self):
        return self.next()

    def __eq__(self, other):
        return self.__static_hash == other.__static_hash and \
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
        if self.__it is None:
            it.__it = None
        elif self.__idx > -1:
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
            if self.__it is None:
                done = True
                item = None
            else:
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
                            self.__it = None
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
                    val, s = self.__commands[i].op(item, done, buffer, self)
                    if not done:
                        if s is False or s == r's':  # skip
                            is_skip = True
                            break
                        elif s == r'r':  # repeat
                            continue
                    if s is True or s == r'n':  # don't change
                        pass
                    elif s is None or s == r'd':  # done
                        raise StopIteration
                    elif (isinstance(val, Iterable) and
                          (s == list or s == r'l')):  # list
                        if not done and len(buffer) > 0:
                            buffer.pop()
                        it = Iterator(val, self.__it)
                        it.__command = i + 1
                        self.__it = it
                        # note: clear buffer is operation duty
                        is_skip = True
                    else:  # value, s == NotImplemented
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

    # controlls

    def obj_strid(self):
        if isinstance(self.__obj, string_types):
            return self.__obj
        elif isinstance(self.__obj, Number) or self.__obj is None:
            return str(self.__obj)
        return str(id(self.__obj))

    def obj_iter(self):
        if isinstance(self.__obj, Iterator):
            it = self.__obj.clone()
            it.reset()
        elif isinstance(self.__obj, Iterable):
            return iter(self.__obj)
        elif self.__obj is None:
            return None
        return iter((self.__obj))

    def reset(self):
        self.__command = None
        self.__it = self.obj_iter()
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

    def add_command(self, cid, f, done_exit=True, cached=None, hash_add=None):
        self.__memo_hash = None
        self.__commands.append(Command(cid, f,
                                       done_exit,
                                       self.__cached if cached is None
                                       else bool(cached),
                                       self.__cache_items,
                                       self.__cache_min,
                                       self.__cache_max,
                                       hash_add))
        return self

    # functional

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
            return val, val != value
        return self.add_command(r'remove', inner)

    def removeList(self, vallist):
        if not isinstance(vallist, Iterable):
            return self.remove(vallist)

        def inner(val, done, buffer, it):
            return val, val not in vallist
        return self.add_command(r'remove', inner)

    def groupby(self, f=lambda v, b, s: v, recursive=True, swither_inc=False):
        root = Ptr([])
        st = Ptr([None])
        cur = Ptr(TreePtr(root.p))

        # False = None states
        # NotImplemented = prevues state
        def getNewState(done, f, val, buf, last):
            newstate = None
            if not done:
                newstate = f(val, buf, last)
            if newstate is False:
                newstate = None
            elif newstate == NotImplemented:
                newstate = st.p[-2] if last is not None else None
            return newstate

        def clearState():
            del st.p[1:]
            ret = root.p
            root.p = cur.p.clear([])
            return ret, list

        def changeCurrent(mode, last):
            if mode:  # up
                cur.p = cur.p.parent
            else:  # down or liner
                if mode is None or last is None:
                    cur.p = TreePtr([], cur.p)
                else:
                    cur.p = TreePtr([], cur.p.parent)
                cur.p.parent.p.append(cur.p.p)

        if recursive:
            def changeState(last, newstate):  # tree
                if last is not None and st.p[-2] == newstate:  # up
                    st.p.pop()
                    return True
                # else - down
                st.p.append(newstate)
                return None
        else:
            def changeState(last, newstate):  # liner
                if last is None:
                    st.p.append(newstate)
                else:
                    st.p[-1] = newstate
                return False

        if swither_inc:
            def switch(newstate, done, buf, last):
                if newstate is None:  # state -> None
                    cur.p.p.append(buf.pop())
                    return clearState()
                # else state -> state or  # None -> state
                mode = changeState(last, newstate)
                if mode:
                    cur.p.p.append(buf.pop())
                    changeCurrent(mode, last)
                else:
                    changeCurrent(mode, last)
                    cur.p.p.append(buf.pop())
                return None, False  # skip
        else:
            def switch(newstate, done, buf, last):
                if newstate is None:  # state -> None
                    if done:
                        cur.p.p.append(buf.pop())
                        ret = clearState()
                    else:
                        ret = clearState()
                        ret[0].append(buf.pop())
                    return ret
                # else - state -> state or  # None -> state
                changeCurrent(changeState(last, newstate), last)
                cur.p.p.append(buf.pop())
                return None, False  # skip

        def inner(val, done, buf, it):
            last = st.p[-1]
            buflen = len(buf)

            # is end
            if done and buflen == 0:
                if len(root.p) > 0:
                    return clearState()
                return None, None

            newstate = getNewState(done, f, val, buf, last)

            # state not changed
            if last == newstate:
                if newstate is None:
                    return buf.pop(), NotImplemented
                return None, False  # skip

            # change state
            cur.p.p.extend(buf[0:-1])
            del buf[0:-1]

            return switch(newstate, done, buf, last)

        return self.add_command(r'groupby', inner, False, False)

    def cahin(self, *args):
        if len(args) <= 0:
            return self

        def unpack():
            for i in args:
                if isinstance(i, Iterable):
                    yield i, list
                else:
                    yield i, NotImplemented
            yield None, None

        def inner(val, done, buffer, it):
            if done:
                return unpack()
            return val, NotImplemented
        return self.add_command(r'cahin', inner, False)

    def scan(self, f):
        def inner(val, done, buffer, it):
            return f(val), list
        return self.add_command(r'scan', inner)

    def store(self):
        stored_commands = self.clone()
        self.__commands = []

        @cache_cached(None, None, None)
        def inner(val, done, buffer, it):
            for i in stored_commands:
                yield i, NotImplemented
            yield None, None
        return self.add_command(r'store', inner, False, False)

    def generator(self, f):
        def inner(val, done, buffer, it):
            return f(), NotImplemented
        return self.add_command(r'generator', inner, False)

    def toempty(self):
        def inner(val, done, buffer, it):
            return None, None
        return self.add_command(r'toempty', inner, False, False)

    # if n == None then infinity
    def cycle(self, n=None):
        is_int = isinstance(n, int)
        if is_int and n == 1:
            return self

        base = []
        p = None
        if is_int and n > 0:
            p = Ptr(n)

            def inner(val, done, buffer, it):
                if done:
                    if p.p == 1:
                        return None, None
                    p.p -= 1
                    return base, list
                base.append(val)
                return val, NotImplemented
        elif n is None:
            def inner(val, done, buffer, it):
                if done:
                    return base, list
                base.append(val)
                return val, NotImplemented
        else:  # n <= 0
            return self.toempty()

        return self.add_command(r'cycle', inner, False, None, p)

    # if n == None then infinity
    def repeat(self, n=None):
        base = []
        is_c = Ptr(True)
        p = None
        if isinstance(n, int) and n > 0:
            p = Ptr(n)

            def inner(val, done, buffer, it):
                if done:
                    if is_c.p:
                        if len(buffer) > 0:
                            base.extend(buffer[:])
                            del buffer[:]
                        is_c.p = False
                    if p.p > 0:
                        p.p -= 1
                        return base, NotImplemented
                    return None, None
                return None, False  # skip
        elif n is None:
            def inner(val, done, buffer, it):
                if done:
                    if is_c.p:
                        if len(buffer) > 0:
                            base.extend(buffer[:])
                            del buffer[:]
                        is_c.p = False
                    return base, NotImplemented
                return None, False  # skip
        else:  # n <= 0 or other
            return self.toempty()

        return self.add_command(r'repeat', inner, False, None, p)

    def takewhile(self, n=None):
        p = None
        if isinstance(n, int) and n > 0:
            p = Ptr(n)

            def inner(val, done, buffer, it):
                if p.p == 0:
                    return None, None
                p.p -= 1
                return val, NotImplemented
        elif six_callable(n):
            def inner(val, done, buffer, it):
                if n(val):
                    return val, NotImplemented
                return None, None
        else:  # n <= 0 or other
            return self.toempty()

        return self.add_command(r'takewhile', inner, True, None, p)

    def fill(self, l, item):
        p = None
        if isinstance(l, int) and l > 0:
            p = Ptr(0)
            getItem = item
            if isinstance(item, Iterable):
                def gen():
                    for i in item:
                        yield i
                getItem = gen
            if six_callable(getItem):
                def inner(val, done, buffer, it):
                    if p.p == l:
                        return None, None
                    p.p += 1
                    if done:
                        return getItem(), NotImplemented
                    return val, NotImplemented
            else:
                def inner(val, done, buffer, it):
                    if p.p == l:
                        return None, None
                    p.p += 1
                    if done:
                        return item, NotImplemented
                    return val, NotImplemented
        else:  # l <= 0 or other
            return self.toempty()

        return self.add_command(r'fill', inner, False, None, p)

    def zip(self, f, *args):
        def unpack():
            for i in args:
                if isinstance(i, Iterable):
                    yield iter(i)
                else:
                    yield iter((i))
        iters = [i for i in unpack()]

        if self.__obj is not None:
            def inner(val, done, buffer, it):
                vals = [val]
                for it in iters:
                    try:
                        vals.append(next(it))
                    except StopIteration:
                        return None, None
                return f(*vals), NotImplemented
        else:
            def inner(val, done, buffer, it):
                vals = []
                for it in iters:
                    try:
                        vals.append(next(it))
                    except StopIteration:
                        return None, None
                return f(*vals), NotImplemented
        return self.add_command(r'zip', inner,
                                self.__obj is not None,
                                None, iters)

    def combine(self, n=2, permutations=True, recurrence=True):
        if not isinstance(n, int) or n < 1:
            return self.toempty()
        elif n == 1:
            return self

        base = []
        bl = Ptr(0)
        limit = Ptr(None)
        skip = None
        r = xrange(n)

        if permutations and recurrence:
            # placement with recurrence
            def check():  # bl**n
                limit.p = bl.p**n

            def comb(buf, l, index):  # n: 2 ... infinity
                for _ in r:
                    i = index % l.p
                    index = index // l.p
                    yield buf[i]
        elif permutations:
            # placement without recurrence
            skip = n

            def check():  # bl! / (bl - n)!
                k = (bl.p if n > bl.p else n)
                limit.p = fac(bl.p) // fac(bl.p - k)

            '''def single(buf, l, index):  # n: 2 ... bl
                for i in r:
                    if i == l.p:
                        break
                    yield buf[(index + i) % l.p]

            def comb(buf, l, index):'''

        elif recurrence:
            # combinations with recurrence
            def check():  # (bl + n - 1)! / (bl - 1)! * n!
                limit.p = fac(bl.p + n - 1) // fac(bl.p - 1) * fac(n)

            '''def comb(buf, l, index):  # n: 2 ... infinity
                for _ in r:
                    i = index % l.p
                    index = index // l.p
                    yield buf[i]'''
        else:  # not permutations and not recurrence
            # combinations without recurrence
            skip = n

            def check():  # bl! / (bl - n)! * n!
                k = (bl.p if n > bl.p else n)
                limit.p = fac(bl.p) // fac(bl.p - k) * fac(k)

            def comb(buf, l, index):  # n: 2 ... bl
                for i in r:
                    if i == l.p:
                        break
                    yield buf[(index + i) % l.p]

        def inner(val, done, buffer, it):
            check(done)
            if not done:
                bl.p += 1
                base.append(val)
                if skip is not None and bl.p < skip:
                    return None, False  # skip
            elif limit.p is None:
                limit.p = check()
            if bl.p > 0 and (limit.p is None or it.__idx < limit.p - 1):
                return ((i for i in comb(base, bl, it.__idx + 1)),
                        NotImplemented)
            return None, None

        return self.add_command(r'combine', inner, False)


if __name__ == r'__main__':
    pass
