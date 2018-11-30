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

from .tokenizer import Token

# LALR(1)
class GrammarItem(Token):
    def __init__(self, tokens, name=None, item_type = r'list', info = {}, types = [], state = None):
        super(GrammarItem, self).__init__(None, types, state)

        self.type = r'grammar'

        self.tokens = tokens
        self.name = name
        self.item_type = item_type
        self.info = info

        self.data = []

        '''self.mod = lambda v: False

        if self.mod == r'list':
            def listFunc(v, itPtr, p):
                if (!v.done && (pos == self.op.lenght))
                    return false;
                elif (pos == self.op.lenght)
                    return true;

                if self.check(v, itPtr, pos):
                    return r'continue'
                return False

            self.mod = listFunc
        }

        case 'repeat':
        {
            this.mod = fn(v, itPtr, p)
            {
                if (v.done)
                    return pos != 0;

                if (self.check(v.value, itPtr, 0))
                {
                    if (!_.isUndef(self.data['delimetr']) && !_.empty(self.data['delimetr']))
                    {
                        var nextIt = _.clone(itPtr);
                        nextIt.next();
                        var delimIt = _.clone(nextIt);
                        if (nextIt.next().value != self.data['delimetr'])
                            return pos != 0;
                        itPtr.set(delimIt);
                    }
                    return 'continue';
                }

                return pos != 0;
            }
            break;
        }

        case 'or':
        {
            self.mod = fn(v, itPtr, p)
            {
                if (v.done || pos == self.op.lenght)
                    return false;
                if (self.check(v.value, it, pos))
                    return true;
                return 'continue';
            }
            break;
        }

        case 'maybe':
        {
            self.mod = fn(v, itPtr, p)
            {
                if (!v.done)
                {
                    var nextIt = _.clone(itPtr);
                    if (self.check(v.value, nextIt, 0))
                    {
                        itPtr.set(nextIt);
                        return true;
                    }
                }

                return true;
            }
            break;
        }

        default:
            break;'''
    
    def part(self, data):
        return self.check(data, True)

    def __check(self, v, nextIt, context, is_part = False):
        token = self.tokens[context[r'pos']]
        if isinstance(token, GrammarItem):
            context[r'it'] = nextIt
            if token.check(context[r'it'], is_part):
                if is_part:        
                    checkEndIt = itertools.tee(context[r'it'])
                    try:
                        next(checkEndIt)
                        return False
                    except StopIteration:
                        pass
                if token.name != None and len(token.name) > 0:
                    if isinstance(self.data, list):
                        self.data = {}
                    self.data[token.name] = token.data
            return True

        if (hasattr(token, r'check') and token.check(v)) or token == v:
            context[r'it'] = nextIt
            if isinstance(self.data, list):
                self.data.append(v)
            return True
        return False

    def check(self, data, is_part = False):
        context = { r'it' : data if hasattr(data, r'__next__') else iter(data), r'pos': 0 }
        while(True):
            nextIt = itertools.tee(context[r'it'])
            try:
                val = next(nextIt)
            except StopIteration:
                if is_part:
                    return True
                return context[r'pos'] + 1 >= len(self.tokens) # its end
            if context[r'pos'] >= len(self.tokens):
                return False
            if not self.__check(val, nextIt, context, is_part):
                break
            context[r'pos'] += 1
        return False