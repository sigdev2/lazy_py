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

    template<class TObject, class TIterator, class TValue>
    class Iterable—pp : public Iterable<TObject, TIterator, TValue>
    {
    public:
        SharedPtrSpec<TIterator> iter()
        {
            SIter* it = new SIter;
            it->it = _obj->begin();
            return SharedPtrSpec<SIter>(it);
        };
        SharedPtrSpec<TValue> next(SharedPtrSpecCRef<TIterator> it)
        {
            Vector<int>::iterator* val = new Vector<int>::iterator(it->it);
            SharedPtrSpec<Vector<int>::iterator> ret(val);
            ++it->it;
            if (it->it == _obj->end())
                throw std::exception();
            return ret;
        };
    };
}

#endif // __LAZY_BIND_CPP_H__