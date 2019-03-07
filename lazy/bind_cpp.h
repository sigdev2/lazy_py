#pragma once

#ifndef __LAZY_BIND_CPP_H__
#define __LAZY_BIND_CPP_H__

#include "defines_cpp.h"

#include "InternalIterator.hpp"

namespace Lazy
{
    class CppContainer : public Contaiter<Vector<int>, int, Vector<int>::iterator>
    {
    protected:
        virtual Vector<int>::iterator _iter() const
        {
            return _source->begin();
        }

        virtual int _next(Vector<int>::iterator& it) const
        {
            ++it;
            if (it == _source->end())
                throw std::exception();
            return *it;
        }
    };
}

#endif // __LAZY_BIND_CPP_H__