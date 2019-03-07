#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "Container.hpp"
#include "Command.hpp"

namespace Lazy
{
    template<class TContainer>
    class InternalIterator
    {
        typedef InternalIterator<TContainer> _Self;
    public:
        // types
        typedef TContainer::TCommand TCommand;
        typedef TContainer::TCommandPtr TCommandPtr;
        typedef TContainer::TRetValue TRetValue;
        typedef TContainer::TCommandRet TCommandRet;
        typedef TContainer::TBuffer TBuffer;
        typedef TContainer::TSourcePtr TObjectPtr;
        typedef TContainer::TItemPtr TValuePtr;
         
        enum EConst
        {
            eReservedCommands = 3
        };

        // constructor/destructor

        InternalIterator(TObjectPtr obj = NULL, _Self* parent = NULL)
           : _idx(0), _obj(obj), _parent(parent), _it(NULL) { _commands.reserve(eReservedCommands); reset(); }
        virtual ~InternalIterator() { }

        // properties

        _Self* parent() const { return _parent; }
        _Self* self() const { return this; }

        // methods

        _Self* reset()
        {
            if (_obj.get() != NULL)
                _it.reset(new STreeIterator(_obj.iter()));
            else
                _it.reset();
            _idx = -1;
            return this;
        }

        _Self* clear()
        {
            _commands.clear();
            _commands.shrink_to_fit();
            _commands.reserve(eReservedCommands);
            return reset();
        }

        _Self* add(TCommandPtr cmd)
        {
            _commands.push_back(cmd);
            return this;
        }

        TValuePtr next()
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
            TContainer::SIterator it;
            SharedPtr<STreeIterator> parent;
            size_t command;

            STreeIterator(const TContainer::SIterator& _it,
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
                old.val = NULL;
            }
            else
            {
                while (true)
                {
                    try
                    {
                        old.done = false;
                        old.val = _it->it.next();
                        break;
                    }
                    catch(...)
                    {
                        old.done = true;
                        if (_it->parent.get() == NULL)
                        {
                            old.val = NULL;
                            _it = NULL;
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
        TContainer _obj;
        SharedPtr<STreeIterator> _it;
        Vector<TCommandPtr> _commands;
        _Self* _parent;
    };
}

#endif // __LAZY_ITERATOR_H__