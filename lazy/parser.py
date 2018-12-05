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
import copy

from .tokenizer import Token, state_tokenizer, LL1TableTokenizer, LL1StateTokenizer

class GrammarContext:
    def __init__(self, data, pos = 0):
        if isinstance(data, GrammarContext):
            self.it = data.it
        if hasattr(data, r'__next__'):
            self.it = data
        else:
            self.it = iter(data)
        self.pos = pos
    
    def __copy__(self):
        return GrammarContext(iter(self), self.pos)

    def __iter__(self):
        self.it, clone_it = itertools.tee(self.it)
        return clone_it
    
    def __next__(self):
        return self.next()
    
    def next(self):
        return next(self.it)
    
    def next_detached(self):
        next_it = iter(self)
        try:
            val = next(next_it)
        except StopIteration:
            return (None, None)
        return (val, next_it)

class ParserData:
    def __init__(self):
        self.tokens = []
        self.properties = {}
        self.is_merged = set()
    
    def empty(self):
        return len(self.tokens) + len(self.properties) + len(self.is_merged) == 0
    
    def simplefy(self):
        val = self
        if val.empty():
            return None
        if len(val.properties) <= 0:
            val = val.tokens
            if len(val) == 1:
                val = val[0]
        return val
    
    def get_property(self, key):
        if key in self.properties:
            val = self.properties[key]
            if isinstance(val, ParserData):
                val = val.simplefy()
            return val
        return None
    
    def add(self, token):
        self.tokens.append(token)
    
    def add_property(self, key, value):
        if isinstance(value, ParserData):
            value = value.simplefy()
        if key in self.properties:
            if key in self.is_merged:
                self.properties[key].append(value)
            else:
                self.properties[key] = [self.properties[key], value]
                self.is_merged.add(key)
        else:
            self.properties[key] = value
        self.tokens.append((self, key))
    
    def update(self, other):
        if not other.empty():
            for key in other.properties.keys():
                first = []
                if key in self.properties:
                    first = self.get_property(key)
                    if not key in self.is_merged:
                        first = [first]
                second = other.get_property(key)
                if not key in other.is_merged:
                    second = [second]
                merged = [x for x in first + second if x != None]
                if len(merged) == 1:
                    merged = merged[0]
                self.properties[key] = merged
            self.is_merged = self.is_merged | other.is_merged

# LALR(1)
class GrammarItem(Token):
    def __init__(self, tokens, name=None, item_type = r'list', info = {}, types = [], state = None):
        super(GrammarItem, self).__init__(None, types, state)

        self.type = r'grammar'
        self.check = self.__check
        self.part = self.__part

        self.tokens = tokens
        self.name = name
        self.item_type = item_type
        self.info = info
    
    def __part(self, data):
        return self.__check(data, True)

    def __token_check(self, ctx, is_part = False, out = ParserData()):
        token = self.tokens[ctx.pos]
        if isinstance(token, GrammarItem):
            recCtx = ctx.__copy__()
            child_out = ParserData()
            if token.check(recCtx, is_part, child_out):
                if is_part:
                    _, is_end = recCtx.next_detached()
                    if is_end != None:
                        return False
                if token.name != None and len(token.name) > 0:
                    out.add_property(token.name, child_out)
                else:
                    out.update(child_out)
                ctx.it = recCtx.it
                return True
            return False
        else:
            val, next_it = ctx.next_detached()
            if next_it == None:
                return is_part
            if (hasattr(token, r'check') and token.check(val)) or token == val:
                if self.name != None and len(self.name) > 0:
                    out.add(val)
                ctx.it = next_it
                return True
        return False
    
    def __op(self, context, l, is_part, out = ParserData()):
        if self.item_type == r'or':
            if self.__token_check(context, is_part, out):
                return True
        elif self.item_type == r'repeat':
            if self.__token_check(context, is_part, out):
                if context.pos + 1 == l:
                    delim, delim_it = context.next_detached()
                    if delim == self.info[r'delimetr']:
                        context.pos = -1
                        context.it = delim_it
                    else:
                        return True
            else:
                return False
        elif self.item_type == r'maybe':
            self.__token_check(context, is_part, out)
            return True
        else: # self.item_type == r'list'
            if self.__token_check(context, is_part, out):
                if context.pos + 1 == l:
                    return True
            else:
                return False
        
        return None

    def __check(self, data, is_part = False, out = ParserData()):
        context = GrammarContext(data)
        l = len(self.tokens)
        while True:
            if context.pos >= l:
                break
            ret = self.__op(context, l, is_part, out)
            if ret != None:
               return ret
            context.pos += 1
        return False

class Grammar(GrammarItem):
    def __init__(self, text):
        super(Grammar, self).__init__(self.__parse(text), r'root')
    
    def __parse(self, text):
        screened = [Token(r'\/'),
            Token(r'\='),
            Token(r'\;'),
            Token(r'\|'),
            Token(r'\{'),
            Token(r'\}')]
        exclude_tokens = [Token(r'#', [r'start'], [r'comment']),
            Token(r'\n', [r'end'], [r'comment']),
            Token(r'/', [r'start', r'end'], [r'regexp']),
            Token([r'?', r'='])]
        table = [
            [r'=', { r'none' : r'list' }],
            [r'?=', { r'none' : r'maybe' }],
            [r';', { r'maybe' : r'none', r'list' : r'none' }]]
        
        repeat_tokens = [Token(r'{', [r'start'], [r'delimetr']),
            Token(r'}', [r'end'], [r'delimetr'])]

        tokenizer = state_tokenizer(text, exclude_tokens + screened)
        tokenizer = iter(tokenizer).filter(lambda x: x[0] != r'#')
        tokenizer = LL1TableTokenizer(tokenizer, table, True)

        buffer = r''
        last = None
        terms = {}
        for token in tokenizer:
            if r''.join(token).strip() == r'':
                continue
            if (token[0] == r'=' or token[0] == r'?=') and token[-1] == r';':
                term_name = buffer
                to_out = term_name[0] == r':'
                if to_out:
                    term_name = term_name[1:]
                buffer = r''
                if term_name.find(r' ') != -1 or term_name in terms:
                    continue

                term_type = r'list'
                tokens = []
                or_buffer = []
                repeat_token = None
                for term in LL1StateTokenizer(token[1:-1], repeat_tokens):
                    if term.strip() == r'':
                        continue
                    elif term[0] == r'{' and term[-1] == r'}':
                        repeat_token = term[1:-1]
                        continue
                    elif term == r'|':
                        term_type = r'or'
                        tokens.append(GrammarItem(or_buffer))
                        or_buffer = []
                        continue

                    for sch in screened:
                        if term == sch.token:
                            term = sch.token[1:]
                            break

                    if term in terms:
                        or_buffer.append(terms[term])
                    else:
                        or_buffer.append(Token(term))
                if len(or_buffer) > 0:
                    if term_type == r'or':
                        tokens.append(GrammarItem(or_buffer))
                    else:
                        tokens = or_buffer
                
                if repeat_token != None: # is repeat
                    if len(tokens) > 1 or term_type == r'or':
                        tokens = [GrammarItem(tokens, None, term_type)]
                    term_type = r'repeat'

                if token[0] == r'?=': # is maybe
                    if len(tokens) > 1 or term_type != r'list':
                        tokens = [GrammarItem(tokens, None, term_type)]
                    term_type = r'maybe'

                last = GrammarItem(tokens, term_name if to_out else None, term_type, {} if repeat_token == None else {r'delimetr' : repeat_token})
                terms[term_name] = last
            else:
                buffer += r''.join(token)
        return [] if last == None else [last]

if __name__ == r'__main__':
    pass