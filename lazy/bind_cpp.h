#pragma once

#ifndef __LAZY_BIND_CPP_H__
#define __LAZY_BIND_CPP_H__

#include "defines.h"

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
        it = new SIter;
        it->it = obj.begin();
        return SharedPtrSpec<SIter>(it);
    }

    template<typename TIterator, typename TValue>
    SharedPtrSpec<int> next(SharedPtrSpecCRef<SIter> it)
    {
        SharedPtrSpec<int> ret(it->it);
        ++it->it;
        return ret;
    }
}

typedef Lazy::Iterator<Vector<int>, Vector<int>::iterator, int> TVecIterator;

#endif // __LAZY_BIND_CPP_H__