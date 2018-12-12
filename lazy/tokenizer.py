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

import re
import copy

from .lazy import IteratorEx, Sublist

class Token:
    def __init__(self, token = None, types = [], state = None):
        self.state = state
        self.types = set(types)
        self.set_token(token)
    
    def set_token(self, token):
        if token != None:
            try:
                rx_obj = re._pattern_type
            except:
                rx_obj = re.Pattern
            if callable(token):
                self.check = token
                self.part = token
                self.type = r'func'
            elif isinstance(token, rx_obj):
                self.type = r'rx'
                self.check = lambda v: token.match(r''.join(v) if isinstance(v, list) else v)
                self.part = lambda v: token.match(r''.join(v) if isinstance(v, list) else v)
            elif isinstance(token, list) and len(token) == 2 and isinstance(token[0], rx_obj) and isinstance(token[1], rx_obj):
                self.check = lambda v: token[0].match(r''.join(v) if isinstance(v, list) else v)
                self.part = lambda v: token[1].match(r''.join(v) if isinstance(v, list) else v)
                self.type = r'rx'
            elif isinstance(token, list) and len(token) == 2 and callable(token[0]) and callable(token[1]):
                self.type = r'func'
                self.check = token[0]
                self.part = token[1]
            elif len(token) > 2 and token[0] == r'/' and token[-1] == r'/':
                self.type = r'rx'
                rx = re.compile(token[1:-1])
                self.check = lambda v: rx.match(r''.join(v) if isinstance(v, list) else v)
                self.part = lambda v: rx.match(r''.join(v) if isinstance(v, list) else v)
            elif isinstance(token, list) and len(token) == 2 and len(token[0]) > 2 and token[0][0] == r'/' and token[0][-1] == r'/' and len(token[1]) > 2 and token[1][0] == r'/' and token[1][-1] == r'/':
                self.type = r'rx'
                rx1 = re.compile(token[0][1:-1])
                rx2 = re.compile(token[1][1:-1])
                self.check = lambda v: rx1.match(r''.join(v) if isinstance(v, list) else v)
                self.part = lambda v: rx2.match(r''.join(v) if isinstance(v, list) else v)
            elif isinstance(token, list):
                self.type = r'list'
                self.check = lambda v: r''.join(token) == r''.join(v)
                self.part = lambda v: r''.join(token[:len(v)] if isinstance(v, list) else token[:1]) == r''.join(v)
            else:
                self.type = r'str'
                self.check = lambda v: token == (r''.join(v) if isinstance(v, list) else v)
                self.part = lambda v: token.startswith(r''.join(v) if isinstance(v, list) else v)
        if self.state == None:
            self.state = token
        self.token = token

    def has(self, typeName):
        return typeName in self.types
    def add(self, typeName):
        return self.types.add(typeName)
    def __len__(self):
        return len(self.token)

class Grouper(object):
    def __init__(self, s):
        self.source = s
    def bufferize(self, buff, done):
        if len(buff) == 0:
            return False
        if len(buff) == 1:
            return buff[0]
        if done:
            return r''.join(buff)
        last = buff.pop(-1)
        return Sublist([r''.join(buff), last])
    def filter(self, value, buffer):
        return True
    def __iter__(self):
        return IteratorEx(self.source).group(
            lambda v, b: self.filter(v, b),
            lambda x, d: self.bufferize(x, d))  

class Wordizer(Grouper):
    def filter(self, value, buffer):
        return '\'";:.,></?|\\=-+)({}[]*&^%$#@!`~\t\n\r '.find(value) <= -1

# LL(1)
class LL1StateTokenizer(Grouper):
    def __init__(self, s, l):
        super(LL1StateTokenizer, self).__init__(s)
        self.__list = l
    
    def bufferize(self, buff, done):
        if len(buff) == 0:
            return False
        if len(buff) == 1:
            return buff[0]
        return r''.join(buff)

    def  __iter__(self):
        local = { r'state' : r'none' }
        def stateFilter(v, buff):
            for val in self.__list:
                if val.check(v):
                    if local[r'state'] == r'none':
                        if r'start' in val.types:
                            local[r'state'] = val.state
                            break
                    else:
                        if r'end' in val.types and len(set(local[r'state']) & set(val.state)) > 0:
                            local[r'state'] = r'none'
                            break
            return local[r'state'] != r'none'

        return IteratorEx(self.source).group(stateFilter, lambda x, d: self.bufferize(x, d))

# LL(1)
class LL1TableTokenizer(Grouper):
    def __init__(self, s, table, recursive = False):
        super(LL1TableTokenizer, self).__init__(s)
        self.__table = table
        self.__recursive = recursive

    def __compileStackedBuffer(self, buff, allstak=False):
        if len(buff) <= 2:
            return buff
        if self.__recursive:
            buff[-2].append(buff.pop())
        else:
            buff[-2] += buff.pop()
        if allstak:
            return self.__compileStackedBuffer(buff, allstak)
        return buff

    def  __iter__(self):
        local = { r'stack' : [r'none'], r'stack_buffer' : [[]], r'up': None }
        def stateFilter(v, buff):
            local[r'up'] = None
            stack = local[r'stack']
            buffer = local[r'stack_buffer']
            old_state = stack[-1]
            for val in self.__table:
                token = val[0]
                if (hasattr(token, r'check') and token.check(v)) or token == v:
                    stateTable = val[1]
                    newstate = old_state
                    if callable(stateTable):
                        newstate = stateTable(v, old_state)
                    elif old_state in stateTable:
                        newstate = stateTable[old_state]
                    if old_state != newstate:
                        if old_state == r'none':
                            stack.append(newstate)
                            buffer.append([])
                            local[r'up'] = True
                        else:
                            if newstate == r'none':
                                stack.clear()
                                stack.append(r'none')
                                self.__compileStackedBuffer(buffer, True)
                                local[r'up'] = False
                            elif len(stack) > 1 and stack[-2] == newstate:
                                stack.pop()
                                self.__compileStackedBuffer(buffer)
                                local[r'up'] = False
                            else:
                                stack.append(newstate)
                                buffer.append([])
                                local[r'up'] = True
                        return False
                    break
            return old_state != r'none'
    
        def bufferFunc(buff, done):
            if len(buff) == 0:
                return False
            buffer = local[r'stack_buffer']
            if len(buffer) == 0:
                return False
            top_buff = buffer[-1]
            if local[r'stack'][-1] == r'none':
                if len(buffer) > 0 and len(top_buff) > 0:
                    top_buff += buff
                    if self.__recursive:
                        out = copy.deepcopy(top_buff)
                    else:
                        out = r''.join(top_buff)
                    buffer.pop()
                    return out
                else:
                    return r''.join(buff)
            else:
                if self.__recursive:
                    if local[r'up'] == None:
                        top_buff += buff
                    elif local[r'up'] == True:
                        buffer[-2] += buff[:-1]
                        top_buff.append(buff[-1])
                    else:
                        top_buff[-1] += buff
                else:
                    top_buff += buff
                
            return False

        return IteratorEx(self.source).group(stateFilter, bufferFunc)

# LL(k)
class LLKTokenizer(Grouper):
    def __init__(self, s, l):
        super(LLKTokenizer, self).__init__(s)
        self.__list = l

    def  __iter__(self):
        local = { r'variants': [] }
        def filterGroup(v, buff):
            variants = local[r'variants']
            # add new buffers
            for val in self.__list:
                if val.part(v):
                    variants.append((val, len(buff) - 1))

            # choose actuals buffers
            new_variants = []
            for val in variants:
                token = val[0]
                buffer = buff[val[1]:]

                if token.part(buffer):
                    if token.check(buffer):
                        variants.clear()
                        variants.append(val)
                        return False # send buffer

                    new_variants.append(val)

            variants.clear()
            variants.extend(new_variants)
            return True # skip
        
        def groupBuffer(buff, done):
            variants = local[r'variants']
            if len(variants) == 0:
                return Sublist(buff)

            val = variants[0]
            buffer = buff[val[1]:]
            data = buff[0:val[1]]
            data.append(r''.join(buffer))
            variants.clear()
            return Sublist(data)
        
        return IteratorEx(self.source).group(filterGroup, groupBuffer)

# LL(k) greedy, but regular grammar is leazy
class LLKGreedyTokenizer(Grouper):
    def __init__(self, s, l):
        super(LLKGreedyTokenizer, self).__init__(s)
        self.__list = l
        
        sort_map = dict()
        func_and_rx = []
        for val in self.__list:
            if hasattr(val, r'__len__'):
                vallen = len(val)
                if not vallen in sort_map:
                    sort_map[vallen] = []
                sort_map[vallen].append(val)
            else:
                func_and_rx.append(val)

        keys = sorted(list(sort_map.keys()), reverse=True)
        self.multi = self.source
        for val in keys:
            self.multi = LLKTokenizer(self.multi, sort_map[val])
        self.multi = LLKTokenizer(self.multi, func_and_rx)

    def __iter__(self):
        return iter(self.multi)


def stateTable(table):
    def calc(key, state):
        for val in table:
            if (hasattr(val[0], r'check') and val[0].check(key)) or key == val[0]:
                if state in val[1]:
                    return val[1][state]
        return state
    return calc

def stringStates(tokens):
    d = {}
    for token in tokens:
        sub_state = r''
        old_state = r'none'
        for ch in token:
            sub_state += ch
            if ch == token[-1]:
                sub_state = r'none'
            if ch in d:
                d[ch][old_state] = sub_state
            else:
                d[ch] = {old_state : sub_state}
            old_state = sub_state

    for ss in tokens:
        if r'/.*/' in d:
            d[r'/.*/'][ss] = r'none'
        else:
            d[r'/.*/'] = {ss : r'none'}

    ret = []
    for k in d.keys():
        ret.append([k, d[k]])
    return stateTable(ret)

def tokenizer(text, tokens):
    return LLKGreedyTokenizer(Wordizer(text), tokens)

def state_tokenizer(text, tokens):
    return LL1StateTokenizer(LLKGreedyTokenizer(Wordizer(text), tokens), tokens)

def table_tokenizer(text, tokens, table, rec=False):
    return LL1TableTokenizer(LL1StateTokenizer(LLKGreedyTokenizer(Wordizer(text), tokens), tokens), table, rec)

if __name__ == r'__main__':
    pass