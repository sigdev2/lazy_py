Lazy calculations for Python
===================================

This Python module realize part of lazy calculations in functional programing paradigm, based on iterators.

Main part of module is class IteratorEx
______________________________

Relised base commands to work with list of items:
 - filter - for filter iterable object items
 - map - for map iterable object items
 - group - for join items by many states to one in items sequance

Example
_______

Base use:

.. code:: python

    import lazy

    text = r'''_tes/*t t'*/ext /*h'g/*'jgh*//*sdfsf*/ /*spec sdfss*/gdfgdfg spec*/ { sdfsdf {sdfsd} jhghg }{ sdfsdf {sdfsd} jhghg }somefunc(sdfs(dfsd(f))'sdfsdf)') j' kjhkj /* hlkjlkj 'hk*/jh'''
    
    lo = lazy.IteratorEx(text)

Use methods:

.. code:: python

    lo.map(lambda x : x + ' ')

.. code:: python

    lo.filter(lambda x : False)

.. code:: python
    
    def bufferize(buff, done):
        if len(buff) == 0:
            return False
        if len(buff) == 1:
            return buff[0]
        if done:
            return r''.join(buff)
        last = buff.pop(-1)
        return lazy.Sublist([r''.join(buff), last])
 
    lo.group(lambda v, b : '\'";:.,></?|\\=-+)({}[]*&^%$#@!`~\t\n\r '.find(v) <= -1, bufferize)
