#pragma once

#ifndef __LAZY_CONTAINER_H__
#define __LAZY_CONTAINER_H__

#include "Command.hpp"

namespace Lazy
{
    template<typename TSource, typename TItem, typename TExternalPtr>
    struct check_external_ptr
    {
        typedef TExternalPtr<TItem> TItemPtr;
        typedef TExternalPtr<TSource> TSourcePtr;

        typedef Command<TItemPtr> TCommand;
        typedef TExternalPtr<TCommand> TCommandPtr;
    };

    template<typename TSource, typename TItem>
    struct check_external_ptr<TSource, TItem, void>
    {
        typedef TItem* TItemPtr;
        typedef TSource* TSourcePtr;

        typedef Command<TItemPtr> TCommand;
        typedef TCommand* TCommandPtr;
    };

    template<typename TSource, typename TItem, typename TIterator, class TExternalPtr = void>
    class Contaiter
    {
        typedef Contaiter<TSource, TItem, TIterator, TExternalPtr> _Self;
    public:
        typedef TItem TItem;
        typedef TSource TSource;

        typedef check_external_ptr<TSource, TItem, TExternalPtr> TExternalChecker;

        typedef TExternalChecker::TItemPtr TItemPtr;
        typedef TExternalChecker::TSourcePtr TSourcePtr;

        typedef TExternalChecker::TCommand TCommand;
        typedef TExternalChecker::TCommandPtr TCommandPtr;

        typedef TCommand::SRetValue TRetValue;
        typedef TCommand::SCommandRet TCommandRet;
        typedef TCommand::TBuffer TBuffer;

        struct SIterator
        {
            SIterator(const SharedPtr<_Self>& obj)
                : _obj(obj), it(obj->_iter())
            { }

            TItemPtr next() { return _obj->_next(it); }
            
            TIterator it;
        private:
            SharedPtr<_Self> _obj;
        };

        Container(const TSourcePtr& source = NULL) : _source(source) {}
        virtual ~Conatiner() {}

        TSourcePtr get() const { return _source; }

        SIterator iter() const { return SIterator(this); };

    protected:
        virtual TIterator _iter() const = 0;
        virtual TItemPtr _next(TIterator& it) const = 0;

        TSourcePtr _source;
    };
}

#endif // __LAZY_CONTAINER_H__