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
        return SharedPtrSpec<PyObject>(boost::python::borrowed(PyObject_GetIter(obj.get())));
    }

    template<typename TIterator, typename TValue>
    SharedPtrSpec<PyObject> next(SharedPtrSpecCRef<PyObject> it)
    {
        return SharedPtrSpec<PyObject>(boost::python::borrowed(PyIter_Next(it.get())));
    }

    typedef Lazy::InternalIterator<PyObject, PyObject, PyObject> TInternalIterator;
}

#endif // __LAZY_BIND_PYTHON_H__