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

from os.path import realpath
from os.path import dirname
import sys
sys.path.insert(0, realpath(dirname(realpath(__file__)) + r'/..'))
import lazy


class TestLazyIterator(unittest.TestCase):
    def test_map(self):
        text = r'word1,word2,word3'
        out = r''
        for ch in lazy.Iterator(text).map(lambda x: x + r'n'):
            out += ch
        self.assertEqual(out, r'wnonrndn1n,nwnonrndn2n,nwnonrndn3n')

    def test_filter(self):
        text = r'word1,word2,word3'
        out = r''
        for ch in lazy.Iterator(text).filter(lambda x: x != r'o'):
            out += ch
        self.assertEqual(out, r'wrd1,wrd2,wrd3')

    def test_remove(self):
        text = r'word1,word2,word3'
        out = r''
        for ch in lazy.Iterator(text).remove([r'o', r'd']):
            out += ch
        self.assertEqual(out, r'wr1,wr2,wr3')

    def test_group(self):
        text = r'word1word2word3'
        out = []
        for ch in lazy.Iterator(text).groupby(lambda x, b, s: not x.isdigit()):
            if isinstance(ch, list):
                out.append(r''.join(ch))
            else:
                out.append(ch)
        self.assertEqual(out, [r'word', r'1', r'word', r'2', r'word', r'3'])

    def test_liner_group(self):
        text = r'a{[()][(][)]}b'
        out = []

        def states(ch, b, s):
            if ch == r'(' or ch == r')':
                return r'c_bracket'
            if ch == r'{' or ch == r'}':
                return r's_bracket'
            if ch == r'[' or ch == r']':
                return r'k_bracket'
            return None

        for ch in lazy.Iterator(text).groupby(states, recursive=False):
            out.append(ch)
        self.assertEqual(out, [r'a',
                               [r'{'],
                               [r'['],
                               [r'(', r')'],
                               [r']', r'['],
                               [r'('],
                               [r']', r'['],
                               [r')'],
                               [r']'],
                               [r'}'],
                               r'b'])

    def test_liner_group_swither_include(self):
        text = '"string1"\'string2\''
        text += '"string3\'quoted""string4\'quoted"'
        text += '\'string3"quoted\'\'string4"quoted\''
        out = []

        def states(ch, b, s):
            if (ch == '\'' or ch == r'"') and s is None:
                return ch
            if ch == s:
                return None
            return s

        for ch in lazy.Iterator(text).groupby(states, False, True):
            out.append(r''.join(ch))
        self.assertEqual(out, [r'"string1"', '\'string2\'',
                               '"string3\'quoted"', '"string4\'quoted"',
                               '\'string3"quoted\'', '\'string4"quoted\''])

    def test_recursive_group(self):
        text = r'a{[()][(][)]}[]b'
        out = []

        def states(ch, b, s):
            if ch == r'(' or ch == r')':
                return r'c_bracket'
            if ch == r'{' or ch == r'}':
                return r's_bracket'
            if ch == r'[' or ch == r']':
                return r'k_bracket'
            return None

        for ch in lazy.Iterator(text).groupby(states):
            out.append(ch)
        self.assertEqual(out, [r'a',
                               [r'{',
                                [r'[', [r'(', r')'], r']',
                                 r'[', [r'('], r']',
                                 r'[', [r')'], r']'],
                                r'}',
                                [r'[', r']']],
                               r'b'])

    def test_recursive_group_swither_include(self):
        text = r'a{[()][(][)]}{}b'
        out = []

        def states(ch, b, s):
            if ch == r'(' and s == r'down2':
                return r'down3'
            if ch == r')' and s == r'down3':
                return r'down2'
            if ch == r'[' and s == r'down1':
                return r'down2'
            if ch == r']' and s == r'down2':
                return r'down1'
            if ch == r'{' and s is None:
                return r'down1'
            if ch == r'}' and s == r'down1':
                return None
            return s

        for ch in lazy.Iterator(text).groupby(states, swither_inc=True):
            out.append(ch)
        self.assertEqual(out, [r'a',
                               [r'{',
                                [r'[', [r'(', r')'], r']'],
                                [r'[', [r'(', r']', r'[', r')'], r']'],
                                r'}'],
                               [r'{', r'}'],
                               r'b'])


r"""class TestLazyTokenizer(unittest.TestCase):
    def test_wordize(self):
        text = r'word1_word2_word3=CheckFunc(set="123")'
        out = []
        for word in lazy.tokenizer.Wordizer(text):
            out.append(word)
        self.assertEqual(out, [r'word1_word2_word3', r'=', r'CheckFunc',
            r'(', r'set', r'=', r'"', r'123', r'"', r')'])

    def test_tokenize(self):
        text = r'/*/*/*spec*/spec*/*/'
        tokens = [lazy.tokenizer.Token(r'/*'),
                lazy.tokenizer.Token(r'*/'),
                lazy.tokenizer.Token([r'/', r'*', r'spec']),
                lazy.tokenizer.Token([r'spec', r'*', r'/'])]
        out = []
        for word in lazy.tokenizer.tokenizer(text, tokens):
            out.append(word)
        self.assertEqual(out, [r'/*', r'/*',
            r'/*spec', r'*/', r'spec*/', r'*/'])

    def test_tokenize_liner_state(self):
        text = r'/* comment /*spec "quoted comment */"quoted comment*/ '
        text += r'/*spec text"/*spec "quoted spec comment*/ spec*/'
        tokens = [lazy.tokenizer.Token(r'/*', [r'start'], [r'mult']),
                lazy.tokenizer.Token(r'*/', [r'end'], [r'mult']),
                lazy.tokenizer.Token(r'"', [r'end', r'start'], [r'string']),
                lazy.tokenizer.Token([r'/', r'*', r'spec'],
                                     [r'start'], [r'spec']),
                lazy.tokenizer.Token([r'spec', r'*', r'/'],
                                     [r'end'], [r'spec'])]
        out = []
        for word in lazy.tokenizer.state_tokenizer(text, tokens):
            out.append(word)
        self.assertEqual(out, [r'/* comment /*spec "quoted comment */',
            r'"quoted comment*/ /*spec text"',
            r'/*spec "quoted spec comment*/ spec*/'])

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

        text = r'var b()=somefunc(arg1="somefunc() {}",'
        text += r' arg2 = call_other(")\""), ea)'
        out = []
        for word in lazy.tokenizer.table_tokenizer(text, tokens, table):
            out.append(word)
        self.assertEqual(out, [r'var', r' ', r'b', r'(', r')', r'=',
            r'somefunc(arg1="somefunc() {}", arg2 = call_other(")\""), ea)'])

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
        self.assertEqual(out, [r'global_namespace',
            [r'{', r'namespace1',
                [r'{', r'class', [r'{',
                    r'func1', [r'{', r'var', r' ',
                                     r'var1', r'=', r'"{"', r'}'],
                    r'func2', [r'{', r'var', r' ',
                                     r'var2', r'=', r'"}"', r'}'],
                r'}'],
            r'}']] +
            [r'namespace2',
                [r'{', r'class', [r'{',
                    r'func1', [r'{', r'var', r' ',
                                     r'var1', r'=', r'"{"', r'}'],
                    r'func2', [r'{', r'var', r' ',
                                     r'var2', r'=', r'"}"', r'}'],
                r'}'],
                r'}'],
            r'}']])

class TestLazyParser(unittest.TestCase):
    def test_simple_grammar(self):
        grammar = lazy.parser.Grammar(r'''
            grammar_name = number/\s*/op/\s*/number;
            :op = +;
            :number = /\d/;
            ''')
        text = r'1 + 1'
        out = lazy.parser.ParserData()
        self.assertTrue(grammar.check(text, out))
        ret = -1
        if out.properties[r'op'] == r'+':
            ret = int(out.properties[r'number'][0]) +
                  int(out.properties[r'number'][1])
        self.assertEqual(ret, 2)

    def test_recursive_grammar(self):
        grammar = lazy.parser.Grammar(r'''
            grammar_name = /\d/ next_list;
            next_list ?= space , space grammar_name;
            space ?= /\s+/;
            ''')
        text = lazy.tokenizer.Wordizer(r'1, 2, 3, 4')
        self.assertTrue(grammar.check(text))

    def test_stop_infinity_recursion_grammar(self):
        grammar = lazy.parser.Grammar(r'''
            grammar_name = next_list /\d/;
            # infinity left recursion
            next_list ?= grammar_name space;
            space ?= /\s+/;
            ''')
        text = lazy.tokenizer.Wordizer(r'1 2 3 4')
        self.assertFalse(grammar.check(text))

    def test_grammar_choose(self):
        grammar = lazy.parser.Grammar(r'''
            grammar_name = music3 | music1 | music2;
            space ?= /\s+/;
            # test comment
            music1 = do space re space mi;
            music2 = do space re space si;
            music3 = music1 fa;
            ''')
        text = lazy.tokenizer.Wordizer(r'do re si')
        self.assertTrue(grammar.check(text))
        text = lazy.tokenizer.Wordizer(r'do re mi')
        self.assertTrue(grammar.check(text))
        text = lazy.tokenizer.Wordizer(r'do re mi fa')
        self.assertTrue(grammar.check(text))"""

if __name__ == r'__main__':
    unittest.main(exit=False)
