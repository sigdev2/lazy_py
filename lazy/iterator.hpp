#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "commands.hpp"

namespace Lazy
{
    // globals

    template<typename TObject, typename TIterator>
    SharedPtrSpec<TIterator> iter(SharedPtrSpecCRef<TObject> obj) { _ass(false); return NULL; }
    template<typename TIterator, typename TValue>
    SharedPtrSpec<TValue> next(SharedPtrSpecCRef<TIterator> it) { _ass(false); return NULL; }

    template<class TObject, class TIterator, class TValue>
    class Iterator
    {
    public:
        // types

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

        Iterator(TObject* obj = NULL, Iterator<TObject, TIterator, TValue>* parent = NULL)
           : _idx(0), _obj(obj), _parent(parent), _it(NULL) { _commands.reserve(eReservedCommands); reset(); }
        virtual ~Iterator() { }

        // properties

        Iterator<TObject, TIterator, TValue>* parent() const { return _parent; }

        // methods

        Iterator<TObject, TIterator, TValue>* reset()
        {
            if (_obj.get() != NULL)
                _it.reset(new STreeIterator(iter<TObject, TIterator>(_obj)));
            else
                _it.reset();
            _idx = 0;
            return this;
        }

        Iterator<TObject, TIterator, TValue>* clear()
        {
            _commands.clear();
            _commands.shrink_to_fit();
            _commands.reserve(eReservedCommands);
            return reset();
        }

        Iterator<TObject, TIterator, TValue>*  add(TCommandPtr cmd)
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
                        throw Exception("StopIteration");
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
                            throw Exception("StopIteration");
                        
                        if (ret.code == TCommand::eList)
                        {
                            if (!val.done && !buffer.empty())
                                buffer.pop_back();
                            SharedPtr<STreeIterator> it(new STreeIterator(iter<TValue, TIterator>(ret.val),
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
                        old.val = Lazy::next<TIterator, TValue>(_it->it);
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
        SharedPtrSpec<TObject> _obj;
        SharedPtr<STreeIterator> _it;
        Vector<TCommandPtr> _commands;
        Iterator<TObject, TIterator, TValue>* _parent;
    };
}

#endif // __LAZY_ITERATOR_H__