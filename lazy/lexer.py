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

from .tokenizer import Token, state_tokenizer

class GrammarContext:
    def __init__(self, data, pos = 0):
        self.it = data if hasattr(data, r'__next__') else iter(data)
        self.pos = pos
    
    def __copy__(self):
        copy_it, self.it = itertools.tee(self.it)
        return GrammarContext(copy_it, self.pos)

    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()
    
    def next(self):
        return next(self.it)
    
    def next_detached(self):
        next_it, self.it = itertools.tee(self.it)
        try:
            val = next(next_it)
        except StopIteration:
            return (None, None)
        return (val, next_it)


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

        self.data = []
    
    def __part(self, data):
        return self.__check(data, True)

    def __token_check(self, ctx, is_part = False):
        token = self.tokens[ctx.pos]
        if isinstance(token, GrammarItem):
            recCtx = ctx.__copy__()
            if token.check(recCtx, is_part):
                if is_part:
                    _, is_end = recCtx.next_detached()
                    if is_end != None:
                        return False
                if token.name != None and len(token.name) > 0:
                    if isinstance(self.data, list):
                        self.data = {}
                    self.data[token.name] = token.data
                ctx.it = recCtx.it
                return True
            return False
        else:
            val, next_it = ctx.next_detached()
            if next_it == None:
                return is_part
            if (hasattr(token, r'check') and token.check(val)) or token == val:
                if isinstance(self.data, list):
                    self.data.append(val)
                ctx.it = next_it
                return True
        return False
    
    def __op(self, context, l, is_part):
        if self.item_type == r'or':
            if self.__token_check(context, is_part):
                return True
        elif self.item_type == r'repeat':
            if self.__token_check(context, is_part):
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
            self.__token_check(context, is_part)
            return True
        else: # self.item_type == r'list'
            if self.__token_check(context, is_part):
                if context.pos + 1 == l:
                    return True
            else:
                return False
        
        return None

    def __check(self, data, is_part = False):
        context = GrammarContext(data)
        l = len(self.tokens)
        while True:
            if context.pos >= l:
                break
            ret = self.__op(context, l, is_part)
            if ret != None:
               return ret
            context.pos += 1
        return False

class Grammar(GrammarItem):
    def __init__(self, text):
        super(Grammar, self).__init__(self.__parse(text), r'root')
    
    def __parse(self, text):
        exclude_tokens = [Token(r'#', [r'start'], [r'comment']),
              Token(r'\n', [r'end'], [r'comment']),
              Token(r'/', [r'setart', r'end'], [r'regexp']),
              Token(r'\/'),
              Token(r'\='),
              Token(r'\;')]
        expr_tokens = [Token(r'=', [r'start'], [r'list']),
                Token([r'|', r'='], [r'start'], [r'or']),
                Token([r'?', r'='], [r'start'], [r'maybe']),
                Token([r'@', r'='], [r'start'], [r'repeat']),
                Token(r';', [r'end'], [r'or', r'list', r'maybe', r'repeat'])]
        tokenizer = state_tokenizer(text, exclude_tokens)
        tokenizer = iter(tokenizer).filter(lambda x: x[0] == r'#')
        tokenizer = state_tokenizer(tokenizer, expr_tokens)
        buffer = r''
        first = None
        terms = {}
        for token in tokenizer:
            if (token[0] == r'=' or (token[1] == r'=' and (token[0] == r'|' or token[0] == r'@' or token[0] == r'?'))) and token[-1] == r';':
                term_name = buffer.strip()
                buffer = r''
                if term_name.find(r' ') != -1 or term_name in terms:
                    continue
                tokens = []
                for term in token[1:-1]:
                    if term in terms:
                        tokens.append(terms)
                    else:
                        tokens.append(Token(term))
                if first == None:
                    first = tokens
                    terms[term_name] = self
                    self.name = term_name
                else:
                    terms[term_name] = GrammarItem(tokens)
            else:
                buffer += token
        return [] if first == None else first