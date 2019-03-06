#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "commands.hpp"

namespace Lazy
{
    // globals

    template<class TObject, class TIterator, class TValue>
    class Iterable
    {
    public:
        Iterable(SharedPtrSpecCRef<TObject> obj)
            : _obj(obj) {}
        TObject* get() { return _obj.get(); }
        SharedPtrSpec<TIterator> iter() { _ass(false); return NULL; };
        SharedPtrSpec<TValue> next(SharedPtrSpecCRef<TIterator> it) { _ass(false); return NULL; };
    protected:
        SharedPtrSpec<TObject> _obj;
    };

    template<class TIterable, class TObject, class TIterator, class TValue>
    class InternalIterator
    {
    public:
        // types

        typedef TObject TObject;
        typedef List<SharedPtrSpec<TValue> > TBuffer;
        typedef typename Command<TValue, TBuffer>::SRetValue TRetValue;
        typedef typename Command<TValue, TBuffer>::SCommandRet TCommandRet;
        typedef Command<TValue, TBuffer> TCommand;
        typedef SharedPtr<Command<TValue, TBuffer> > TCommandPtr;
         
        enum EConst
        {
            eReservedCommands = 3
        };

        // constructor/destructor

        InternalIterator(SharedPtrSpecCRef<TObject> obj = NULL, InternalIterator<TIterable, TObject, TIterator, TValue>* parent = NULL)
           : _idx(0), _obj(obj), _parent(parent), _it(NULL) { _commands.reserve(eReservedCommands); reset(); }
        virtual ~InternalIterator() { }

        // properties

        InternalIterator<TIterable, TObject, TIterator, TValue>* parent() const { return _parent; }

        // methods

        InternalIterator<TIterable, TObject, TIterator, TValue>* self()
        {
            return this;
        }

        InternalIterator<TIterable, TObject, TIterator, TValue>* reset()
        {
            if (_obj.get() != NULL)
                _it.reset(new STreeIterator(_obj.iter()));
            else
                _it.reset();
            _idx = 0;
            return this;
        }

        InternalIterator<TIterable, TObject, TIterator, TValue>* clear()
        {
            _commands.clear();
            _commands.shrink_to_fit();
            _commands.reserve(eReservedCommands);
            return reset();
        }

        InternalIterator<TIterable, TObject, TIterator, TValue>*  add(TCommandPtr cmd)
        {
            _commands.push_back(cmd);
            return this;
        }

        SharedPtrSpec<TValue> next()
        {
            TRetValue val(NULL, true);
            TBuffer buffer;
            while (true)
            {
                _get_next(val);

                if (val.done)
                {
                    if (_commands.empty())
                        THROW_STOP_ITERATION;
                }
                else
                {
                    buffer.push_back(val.val);
                }
                
                bool is_skip = false;
                const size_t l = _commands.size();
                for (size_t i = _it->command; i < l; ++i)
                {
                    while (true)
                    {
                        TCommandRet ret = _commands[i]->exec(val, buffer, _idx);
                        
                        if (!val.done)
                        {
                            if (ret.code == TCommand::eSkip)
                            {
                                is_skip = true;
                                break;
                            }
                            if (ret.code == TCommand::eRepeat)
                                continue;
                        }

                        if (ret.code == TCommand::eDone)
                            THROW_STOP_ITERATION;
                        
                        if (ret.code == TCommand::eList)
                        {
                            if (!val.done && !buffer.empty())
                                buffer.pop_back();
                            SharedPtr<STreeIterator> it(new STreeIterator(ret.val.iter(ret.val),
                                                        _it, _it->command + 1));
                            _it = it;
                            // note: clear buffer is operation duty
                            is_skip = true;
                        }
                        else // Command::eNotChanged
                        {
                            val.val = ret.val;
                            if (!val.done && !buffer.empty())
                                buffer.pop_back();
                            buffer.push_back(val.val);
                        }
                        break;
                    }

                    if (is_skip)
                        break;
                }

                if (is_skip)
                    continue;

                break;
            }

            ++_idx;
            return val.val;
        }
    
    private:
        // types

        struct STreeIterator
        {
            SharedPtrSpec<TIterator> it;
            SharedPtr<STreeIterator> parent;
            size_t command;

            STreeIterator(SharedPtrSpecCRef<TIterator> _it = NULL,
                          SharedPtrCRef<STreeIterator> _parent = NULL,
                          size_t _command = 0)
                : it(_it), parent(_parent), command(_command) {}
        };

        // methods

        TRetValue& _get_next(TRetValue& old)
        {
            if (_it.get() == NULL)
            {
                old.done = true;
                old.val.reset();
            }
            else
            {
                while (true)
                {
                    try
                    {
                        old.done = false;
                        old.val = _obj.next(_it->it);
                        break;
                    }
                    catch(...)
                    {
                        old.done = true;
                        if (_it->parent == NULL)
                        {
                            old.val.reset();
                            _it.reset();
                            break;
                        }
                        else
                        {
                            _it = _it->parent;
                        }
                    }
                }
            }

            return old;
        }

        // members

        int _idx;
        TIterable _obj;
        SharedPtr<STreeIterator> _it;
        Vector<TCommandPtr> _commands;
        InternalIterator<TIterable, TObject, TIterator, TValue>* _parent;
    };
}

#endif // __LAZY_ITERATOR_H__