#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "assert.h"

namespace Lazy
{
    template<typename TObject, typename TIterator>
    TIterator* iter(TObject* obj) { assert(false); return NULL; }
    template<typename TIterator, typename TValue>
    TValue* next(TIterator* it) { assert(false); return NULL; }

    template<typename TObject, typename TIterator, typename TValue>
    class Iterator
    {
    public:
        Iterator(TObject* obj = NULL)
           : _idx(0), _obj(obj)
        {
            reset();
        }

        Iterator<TObject, TIterator>* reset()
        {
            if (_obj == NULL)
                _it = NULL;
            else
                _it = iter(_obj);
            _idx = 0;
            return this;
        }

        TValue next()
        {
            
        }
    
    private:
        int _idx;
        TObject* _obj;
        TObject* _it;
    };
}

#endif // __LAZY_ITERATOR_H__