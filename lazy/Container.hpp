#pragma once

#ifndef __LAZY_CONTAINER_H__
#define __LAZY_CONTAINER_H__

namespace Lazy
{
    template<typename TSource, typename TItem, typename TIterator>
    class Contaiter
    {
    public:
        typedef TItem TItem;
        typedef TSource TSource;

        struct SIterator
        {
            SIterator(Contaiter<TSource, TItem, TIterator>* obj)
                : _obj(obj), it(obj->_iter())
            { }

            TItem* next() { return _obj->_next(it); }
            
            TIterator it;
        private:
            Contaiter<TSource, TItem, TIterator>* _obj;
        };

        Container(const TSource& source) : _source(source) {}
        virtual ~Conatiner() {}

        SIterator iter() { return SIterator(this); };

    protected:
        virtual TIterator _iter() = 0;
        virtual TItem* _next(const TIterator& it) = 0;

        TSource& _source;
    };
}

#endif // __LAZY_CONTAINER_H__