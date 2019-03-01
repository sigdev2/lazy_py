#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "defines.h"

#include "commands.hpp"

namespace Lazy
{
    // globals

    template<typename TObject, typename TIterator>
    SharedPtrSpec<TIterator> iter(SharedPtrSpecCRef<TObject> obj) { _ass(false); return NULL; }
    template<typename TIterator, typename TValue>
    SharedPtrSpec<TValue> next(SharedPtrSpecCRef<TIterator> it) { _ass(false); return NULL; }

    template<typename TObject, typename TIterator, typename TValue>
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

        Iterator(SharedPtrSpecCRef<TObject> obj = NULL, Iterator* parent = NULL)
           : _idx(0), _obj(obj), _parent(parent), _it(NULL) { _commands.reserve(eReservedCommands); reset(); }

        // properties

        Iterator* parent() const { return _parent; }

        // methods

        Iterator<TObject, TIterator, TValue>* reset()
        {
            _it.reset(NULL);
            if (_obj.get() != NULL)
                _it.reset(new STreeIterator(iter<TObject, TIterator>(_obj)));
            _idx = 0;
            return this;
        }

        Iterator<TObject, TIterator, TValue>* clear()
        {
            _commands.clear();
            _commands.shrink_to_fit();
            _commands.reserve(eReservedCommands);
            reset();
        }

        Iterator<TObject, TIterator, TValue>*  add(TCommandPtr cmd)
        {
            _commands.push_back(cmd);
        }

        SharedPtrSpec<TValue> next()
        {
            TRetValue val(NULL, true);
            TBuffer buffer;
            while (true)
            {
                _get_next(val);

                if (done)
                {
                    if (self.__commands.empty())
                        throw Exception("StopIteration");
                }
                else
                {
                    buffer.push_back(item);
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
                            if (ret.code == Command::eSkip)
                            {
                                is_skip = true;
                                break;
                            }
                            if (ret.code == Command::eRepeat)
                                continue
                        }

                        if (ret.code == Command::eDone)
                            throw Exception("StopIteration");
                        
                        if (ret.code == Command::eList)
                        {
                            if (!val.done && !buffer.empty())
                                buffer.pop_back();
                            SharedPtr<STreeIterator> it(iter<TValue, TIterator>(ret.val),
                                                        _it, _command + 1);
                            _it.reset(it);
                            // note: clear buffer is operation duty
                            is_skip = true;
                        }
                        else // Command::eNotChanged
                        {
                            item.reset(ret.val)
                            if done or len(buffer) == 0:
                                buffer.append(item)
                            else:
                                buffer[-1] = item
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
            return item;
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

        TRetValue& _get_next(TRetValue& old, SharedPtr<STreeIterator>& it) const
        {
            if (it.get() == NULL)
            {
                old.done = true;
                old.val.reset(NULL);
            }
            else
            {
                while (true)
                {
                    try
                    {
                        old.done = false;
                        old.val.reset(next<TIterator, TValue>(_it->it));
                        break;
                    }
                    catch(...)
                    {
                        old.done = true;
                        if (it->parent == NULL)
                        {
                            old.val.reset(NULL);
                            it.reset(NULL);
                            break;
                        }
                        else
                        {
                            it.reset(it->parent);
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
        Iterator* _parent;
    };
}

#endif // __LAZY_ITERATOR_H__