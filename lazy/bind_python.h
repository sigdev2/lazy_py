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
        // TODO: need ref count ?
        return SharedPtrSpec<PyObject>(PyObject_GetIter(obj));
    }

    template<typename TIterator, typename TValue>
    SharedPtrSpec<PyObject> next(SharedPtrSpecCRef<PyObject> it)
    {
        // TODO: need ref count ?
        return SharedPtrSpec<PyObject>(PyIter_Next(it.get()));
    }
}

#endif // __LAZY_BIND_PYTHON_H__