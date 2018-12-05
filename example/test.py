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

import unittest

import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), r'..')))
import lazy

class TestLazyTokenizer(unittest.TestCase):
    def test_wordize(self):
        text = r'word1_word2_word3=CheckFunc(set="123")'
        out = []
        for word in lazy.tokenizer.Wordizer(text):
            out.append(word)
        self.assertEqual(out, [r'word1_word2_word3', r'=', r'CheckFunc', r'(', r'set', r'=', r'"', r'123', r'"', r')'])

    def test_tokenize(self):
        text = r'/*/*/*spec*/spec*/*/'
        tokens = [lazy.tokenizer.Token(r'/*'),
                lazy.tokenizer.Token(r'*/'),
                lazy.tokenizer.Token([r'/', r'*', r'spec']),
                lazy.tokenizer.Token([r'spec', r'*', r'/'])]
        out = []
        for word in lazy.tokenizer.tokenizer(text, tokens):
            out.append(word)
        self.assertEqual(out, [r'/*', r'/*', r'/*spec', r'*/', r'spec*/', r'*/'])

    def test_tokenize_liner_state(self):
        text = r'/* comment /*spec "quoted comment */"quoted comment*/ /*spec text"/*spec "quoted spec comment*/ spec*/'
        tokens = [lazy.tokenizer.Token(r'/*', [r'start'], [r'mult']),
                lazy.tokenizer.Token(r'*/', [r'end'], [r'mult']),
                lazy.tokenizer.Token(r'"', [r'end', r'start'], [r'string']),
                lazy.tokenizer.Token([r'/', r'*', r'spec'], [r'start'], [r'spec']),
                lazy.tokenizer.Token([r'spec', r'*', r'/'], [r'end'], [r'spec'])]
        out = []
        for word in lazy.tokenizer.state_tokenizer(text, tokens):
            out.append(word)
        self.assertEqual(out, [r'/* comment /*spec "quoted comment */', r'"quoted comment*/ /*spec text"', r'/*spec "quoted spec comment*/ spec*/'])

    def test_tokenize_state_table(self):
        tokens = [lazy.tokenizer.Token(r'/*', [r'start'], [r'mult']),
                lazy.tokenizer.Token(r'*/', [r'end'], [r'mult']),
                lazy.tokenizer.Token(r'\"'),
                lazy.tokenizer.Token(r'somefunc('),
                lazy.tokenizer.Token(r'"', [r'end', r'start'], [r'string'])]

        local = { r'count': 0 }

        def args(val, state):
            if state == r'none':
                if False:
                    if val == r'(':
                        local[r'count'] += 1
                        return r'in_args'
            elif state == r'in_args':
                if val == r'(':
                    local[r'count'] += 1
                elif val == r')':
                    local[r'count'] -= 1
                if local[r'count'] <= 0:
                    return r'none'
            return state
        
        def function(val, state):
            if state == r'none':
                local[r'count'] += 1
                return r'in_args'
            return state
        table = [
            [r'somefunc(', function],
            [r'(', args],
            [r')', args],
        ]

        text = r'var b()=somefunc(arg1="somefunc() {}", arg2 = call_other(")\""), end_arg)'
        out = []
        for word in lazy.tokenizer.table_tokenizer(text, tokens, table):
            out.append(word)
        self.assertEqual(out, [r'var', r' ', r'b', r'(', r')', r'=', r'somefunc(arg1="somefunc() {}", arg2 = call_other(")\""), end_arg)'])

    def test_tokenize_recursive_table(self):
        tokens = [lazy.tokenizer.Token(r'"', [r'end', r'start'], [r'string'])]
        local = { r'count_rec': 0 }
        def recursiveArgs(val, state):
            if val == r'{':
                local[r'count_rec'] += 1
                return r'in_args' + str(local[r'count_rec'])
            elif val == r'}':
                local[r'count_rec'] -= 1
                if local[r'count_rec'] <= 0:
                    return r'none'
                return r'in_args' + str(local[r'count_rec'])
            return state

        table=[
            [r'{', recursiveArgs],
            [r'}', recursiveArgs]
        ]

        out = []
        text = r'namespace1{class{func1{var var1="{"}func2{var var2="}"}}}'
        text += r'namespace2{class{func1{var var1="{"}func2{var var2="}"}}}'
        text = r'global_namespace{' + text + r'}'
        for word in lazy.tokenizer.table_tokenizer(text, tokens, table, True):
            out.append(word)
        self.assertEqual(out, [r'global_namespace', [r'{', r'namespace1', [r'{', r'class', [r'{', r'func1', [r'{', r'var', r' ', r'var1', r'=', r'"{"', r'}'], r'func2', [r'{', r'var', r' ', r'var2', r'=', r'"}"', r'}'], r'}'] , r'}']] +
            [r'namespace2', [r'{', r'class', [r'{', r'func1', [r'{', r'var', r' ', r'var1', r'=', r'"{"', r'}'], r'func2', [r'{', r'var', r' ', r'var2', r'=', r'"}"', r'}'], r'}'] , r'}'], r'}']])

class TestLazyParser(unittest.TestCase):
    def test_simple_grammar(self):
        grammar = lazy.parser.Grammar(r'''
:op = +;
:number = /\d/;
root = number/\s*/op/\s*/number;
''')
        text = r'1 + 1'
        out = lazy.parser.ParserData()
        self.assertTrue(grammar.check(text, False, out))
        ret = -1
        if out.properties[r'op'] == r'+':
            ret = int(out.properties[r'number'][0]) + int(out.properties[r'number'][1])
        self.assertEqual(ret, 2)

if __name__ == r'__main__':
    unittest.main(exit=False)