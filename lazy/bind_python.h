#pragma once

#ifndef __LAZY_BIND_PYTHON_H__
#define __LAZY_BIND_PYTHON_H__

#include "defines_python.h"

#include "iterator.hpp"

namespace Lazy
{
    template<typename TObject, typename TIterator>
    SharedPtrSpec<PyObject> iter(SharedPtrSpecCRef<PyObject> obj)
    {
        SIter* it = new SIter;
        it->it = obj->begin();
        return SharedPtrSpec<SIter>(it);
    }

    template<typename TIterator, typename TValue>
    SharedPtrSpec<PyObject> next(SharedPtrSpecCRef<PyObject> it)
    {
        Vector<int>::iterator* val = new Vector<int>::iterator(it->it);
        SharedPtrSpec<Vector<int>::iterator> ret(val);
        ++it->it;
        return ret;
    }
}

#endif // __LAZY_BIND_PYTHON_H__