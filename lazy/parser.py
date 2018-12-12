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

class Ptr:
    def __init__(self, obj):
        self.value = obj

class GrammarContext:
    def __init__(self, data, pos = 0):
        self.__it = data.__it if isinstance(data, GrammarContext) else Ptr(iter(data))
        self.pos = pos
    
    def __copy__(self):
        return GrammarContext(self.detached(), self.pos)

    def __iter__(self):
        return self.__it.value
    
    def __next__(self):
        return self.next()
    
    def next(self):
        return next(self.__it.value)
    
    def detached(self):
        self.__it.value, copy_it = itertools.tee(self.__it.value)
        return copy_it
    
    def set_iter(self, it):
        self.__it.value = it

    def next_self(self):
        try:
            val = next(self.__it.value)
        except StopIteration:
            return None, False
        return val, True
    
    def next_detached(self):
        next_it = self.detached()
        try:
            val = next(next_it)
        except StopIteration:
            return None, False
        return val, True

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

class GrammarException(Exception):
    r"""Grammar exceptions base class"""
    pass

class MaybeEndOfGrammarException(GrammarException):
    r"""Grammar may end before input"""
    pass

class FailException(GrammarException):
    r"""Fail exceptions base class"""
    pass

class EndOfInputException(FailException):
    r"""Input end before grammar"""
    pass

class NotPartException(FailException):
    r"""Fail exceptions base class"""
    pass

class WrongTokenException(NotPartException):
    r"""Wrong token"""
    pass

class LeftSideRecursionException(NotPartException):
    r"""Left sie infinity recursion"""
    pass

class EndOfGrammarException(NotPartException):
    r"""Grammar end before input"""
    pass

# LALR(1)
class GrammarItem(Token):
    def __init__(self, tokens, name=None, item_type = r'list', info = {}, not_terms = {}, types = [], state = None):
        super(GrammarItem, self).__init__(None, types, state)

        self.type = r'grammar'
        self.check = self.__check
        self.part = self.__part

        self.tokens = tokens
        self.name = name
        self.item_type = item_type
        self.info = info
        self.not_terms = not_terms
    
    def check_raise(self, data, out = None, path = []):
        self.__check_raise(data, out, path)

    def __token_check(self, ctx, out = None, path = []):
        token = self.tokens[ctx.pos]
        if len(self.not_terms) > 0:
            if token.type == r'str' and token.token in self.not_terms:
                if len(path) > 0:
                    finded = [item for item in path if item[1] == token.token]
                    if len(finded) > 0:
                        if len([item for item in finded if item[0] != 0]) <= 0 and ctx.pos == 0:
                            raise LeftSideRecursionException()
                token = self.not_terms[token.token]
        newctx = ctx.__copy__()
        if token.type == r'grammar':
            child_out = None if out == None else ParserData()
            try:
                token.__check_raise(newctx, child_out, path + [(ctx.pos, token.token)] if token.token != None else path)
            except MaybeEndOfGrammarException:
                pass
            if out != None:
                if token.name != None and len(token.name) > 0:
                    out.add_property(token.name, child_out)
                else:
                    out.update(child_out)
            ctx.set_iter(iter(newctx))
        else:
            val, is_valid = newctx.next_self()
            if is_valid == False:
                raise EndOfInputException()
            if (hasattr(token, r'check') and token.check(val)) or token == val:
                if self.name != None and len(self.name) > 0:
                    out.add(val)
                ctx.next_self()
            else:
                raise WrongTokenException()
        if ctx.pos == len(self.tokens) - 1:
            val, is_valid = ctx.next_detached()
            raise MaybeEndOfGrammarException(val, is_valid)
    
    def __check_raise(self, data, out = None, path = []):
        context = GrammarContext(data)
        while True:
            try:
                self.__token_check(context, out, path)
            except GrammarException as e:
                if self.item_type == r'or':
                    if isinstance(e, MaybeEndOfGrammarException):
                        if e.args[1] == False:
                            break
                        raise EndOfGrammarException()
                    if context.pos == len(self.tokens) - 1:
                        raise e
                    continue
                elif self.item_type == r'maybe':
                    break
                else: # self.item_type == r'list' or self.item_type == r'repeat'
                    if isinstance(e, MaybeEndOfGrammarException):
                        if e.args[1]:
                            if self.item_type == r'repeat':
                                if e.args[0] == self.info[r'sep']:
                                    context.pos = 0
                                    context.next_self()
                                    continue
                            raise EndOfGrammarException()
                        break
                    raise e
            finally:
                context.pos += 1
    
    def __check(self, data, out = None, path = []):
        try:
            self.__check_raise(data, out, path)
        except FailException:
            return False
        except GrammarException:
            pass
        return True

    def __part(self, data, out = None, path = []):
        try:
            self.__check_raise(data, out, path)
        except NotPartException:
            return False
        except GrammarException:
            pass
        return True

class Grammar(GrammarItem):
    def __init__(self, grammar):
        super(Grammar, self).__init__(self.__parse(grammar), r'__root__', not_terms={ r'__root__' : self })
    
    def __parse(self, text):
        screened = [Token(r'\/'),
            Token(r'\='),
            Token(r'\;'),
            Token(r'\|'),
            Token(r'\{'),
            Token(r'\}'),
            Token(r'\=')]
        exclude_tokens = [Token(r'#', [r'start'], [r'comment']),
            Token('\n', [r'end'], [r'comment']),
            Token(r'/', [r'start', r'end'], [r'regexp']),
            Token([r'?', r'='])]
        table = [
            [r'=', { r'none' : r'list' }],
            [r'?=', { r'none' : r'maybe' }],
            [r';', { r'maybe' : r'none', r'list' : r'none' }]]
        
        repeat_tokens = [Token(r'{', [r'start'], [r'delimetr']),
            Token(r'}', [r'end'], [r'delimetr'])]

        tokenizer = state_tokenizer(text, exclude_tokens + screened)
        tokenizer = LL1TableTokenizer(tokenizer, table, True)

        buffer = r''
        first = None
        self.not_terms = {}
        for token in iter(tokenizer).filter(lambda x: x[0] != r'#'):
            """if token[0] == r'#':
                continue"""
            if r''.join(token).strip() == r'':
                continue
            if (token[0] == r'=' or token[0] == r'?=') and token[-1] == r';':
                if len(buffer) <= 0:
                    continue
                not_term = buffer
                to_out = not_term[0] == r':'
                if to_out:
                    not_term = not_term[1:]
                buffer = r''
                if not_term.find(r' ') != -1 or not_term in self.not_terms:
                    continue

                item_type = r'list'
                tokens = []
                or_buffer = []
                repeat_sep = None
                for term in LL1StateTokenizer(token[1:-1], repeat_tokens):
                    if term.strip() == r'':
                        continue
                    elif term[0] == r'{' and term[-1] == r'}':
                        repeat_sep = term[1:-1]
                        continue
                    elif term == r'|':
                        item_type = r'or'
                        tokens.append(GrammarItem(or_buffer, not_terms=self.not_terms))
                        or_buffer = []
                        continue

                    for sch in screened:
                        if term == sch.token:
                            term = sch.token[1:]
                            break

                    or_buffer.append(Token(term))
                if len(or_buffer) > 0:
                    if item_type == r'or':
                        tokens.append(GrammarItem(or_buffer, not_terms=self.not_terms))
                    else:
                        tokens = or_buffer
                
                if repeat_sep != None: # is repeat
                    if len(tokens) > 1 or item_type == r'or':
                        tokens = [GrammarItem(tokens, None, item_type, not_terms=self.not_terms)]
                    item_type = r'repeat'

                if token[0] == r'?=': # is maybe
                    if len(tokens) > 1 or item_type != r'list':
                        tokens = [GrammarItem(tokens, None, item_type, not_terms=self.not_terms)]
                    item_type = r'maybe'

                item = GrammarItem(tokens, not_term if to_out else None, item_type, {} if repeat_sep == None else {r'sep' : repeat_sep}, self.not_terms)
                item.token = not_term
                self.not_terms[not_term] = item
                if first == None:
                    first = item
            else:
                buffer += r''.join(token)
        return [] if first == None else [first]

if __name__ == r'__main__':
    pass