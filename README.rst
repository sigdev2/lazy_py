Lazy calculations for Python
===================================

This Python module realize part of lazy calculations in functional programing paradigm, based on iterators.

Main part of module is class IteratorEx
______________________________

Relised base commands to work with list of items:
 - map - for map iterable object items
 - filter - for filter iterable object items
 - remove - ignore items of iterable object
 - groupby - for join items by many states in items sequance

Example
_______

Base use:

.. code:: python

    import lazy

    iterable_object = r'string iterate by symbol'
    for ch in lazy.Iterator(iterable_object):
        print ch

Use methods:
 map:
.. code:: python

    import lazy
    iterable_object = r'string iterate by symbol'
    out = r''
    for ch in lazy.Iterator(iterable_object).map(
      lambda x: r'b' if x == r's' else x):
        out += ch
    print out  # r'btring iterate by bymbol'

..

 - filter:
.. code:: python

    import lazy
    iterable_object = r'string iterate by symbol'
    out = r''
    for ch in lazy.Iterator(iterable_object).filter(lambda x: x != r' '):
        out += ch
    print out  # r'stringiteratebysymbol'

 remove:
.. code:: python

    import lazy
    iterable_object = r'string iterate by symbol'
    out = r''
    for ch in lazy.Iterator(iterable_object).remove(r' ').remove(
      [r'i', r'o', r'a', r'e', r'y']):
        out += ch
    print out  # r'strngtrtbsmbl'

 groupby:
.. code:: python

    import lazy
    iterable_object = r'string iterate by symbol'
    out = []
    for ch in lazy.Iterator(iterable_object).groupby(
      lambda x, b, s: r'space' if x == r' ' else r'word', False):
        out.append(r''.join(ch))
    print out  # [r'string', r' ', r'iterate', r' ', r'by', r' ', r'symbol']
