#pragma once

#ifndef __LAZY_BIND_CPP_H__
#define __LAZY_BIND_CPP_H__

#include "defines_cpp.h"

#include "iterator.hpp"

namespace Lazy
{
    struct SIter
    {
        Vector<int>::iterator it;
    };

    template<typename TObject, typename TIterator>
    SharedPtrSpec<SIter> iter(SharedPtrSpecCRef<Vector<int> > obj)
    {
        SIter* it = new SIter;
        it->it = obj->begin();
        return SharedPtrSpec<SIter>(it);
    }

    template<typename TIterator, typename TValue>
    SharedPtrSpec<Vector<int>::iterator> next(SharedPtrSpecCRef<SIter> it)
    {
        Vector<int>::iterator* val = new Vector<int>::iterator(it->it);
        SharedPtrSpec<Vector<int>::iterator> ret(val);
        ++it->it;
        return ret;
    }
}

#endif // __LAZY_BIND_CPP_H__