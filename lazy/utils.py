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

__all__ = (r'Ptr', r'TreePtr')


class Ptr(object):
    __slots__ = r'p',

    def __init__(self, obj):
        self.p = obj

    def __eq__(self, other):
        return id(self.p) == id(other.p)

    def __hash__(self):
        return hash(id(self.p))


class TreePtr(Ptr):
    __slots__ = r'parent'

    def __init__(self, obj, parent=None):
        super(TreePtr, self).__init__(obj)
        self.parent = parent

    def clear(self, obj=None, parent=None):
        self.p = obj
        self.parent = parent
        return self.p

    def __eq__(self, other):
        return (id(self.p) == id(other.p) and
                id(self.parent) == id(other.parent))

    def __hash__(self):
        return hash(id(self.p) + id(self.parent))
