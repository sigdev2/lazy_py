#pragma once

#ifndef __LAZY_ITERATOR_H__
#define __LAZY_ITERATOR_H__

#include "defines.h"

#include "commands.hpp"

namespace Lazy
{
    template<typename TObject, typename TIterator>
    TIterator* iter(TObject* obj) { _ass(false); return NULL; }
    template<typename TIterator, typename TValue>
    TValue* next(TIterator* it) { _ass(false); return NULL; }

    template<typename TObject, typename TIterator, typename TValue>
    class Iterator
    {
    public:
        Iterator(TObject* obj = NULL, void* parent = NULL)
           : _idx(0), _obj(obj), _parent(parent), _it(NULL)
        {
            reset();
        }

        void* parent() const { return _parent; }

        Iterator<TObject, TIterator, TValue>* reset()
        {
            if (_obj == NULL)
                delete _it;
                _it = NULL;
            else
                delete _it;
                _it = STreeIterator(iter<TObject, TIterator>(_obj));
            _idx = 0;
            return this;
        }

        TValue* next()
        {
            TValue* item = NULL;
            bool done = true
            List buffer;
            while(true)
            {
                if (_it == NULL)
                {
                    done = true;
                    item = NULL;
                }
                else
                {
                    while(true)
                    {
                        try
                        {
                            item = next<TIterator, TValue>(_it.it);
                            done = false;
                            break;
                        }
                        catch(...)
                        {
                            done = true;
                            if (_it._parent == NULL)
                            {
                                item = NULL;
                                delete _it
                                _it = NULL;
                                break;
                            }
                            else
                            {
                                _it.it = _parent;
                            }
                            
                                self.__it = self.__it.__parent
                            else:
                        }
                    }
                }

                if done:
                    if len(self.__commands) == 0:
                        raise StopIteration
                else:
                    buffer.append(item)
                is_skip = False
                start = self.__command
                if hasattr(self.__it, r'_Iterator__command'):
                    start = self.__it.__command
                for i in xrange(len(self.__commands)):
                    while True:
                        if start is not None:
                            i = start
                            start = None

                        if i >= len(self.__commands):
                            break
                        val, s = self.__commands[i].op(item, done, buffer, self)
                        if not done:
                            if s is False or s == r's':  # skip
                                is_skip = True
                                break
                            elif s == r'r':  # repeat
                                continue
                        if s is True or s == r'n':  # don't change
                            pass
                        elif s is None or s == r'd':  # done
                            raise StopIteration
                        elif (isinstance(val, Iterable) and
                            (s == list or s == r'l')):  # list
                            if not done and len(buffer) > 0:
                                buffer.pop()
                            it = Iterator(val, self.__it)
                            it.__command = i + 1
                            self.__it = it
                            # note: clear buffer is operation duty
                            is_skip = True
                        else:  # value, s == NotImplemented
                            item = val
                            if done or len(buffer) == 0:
                                buffer.append(item)
                            else:
                                buffer[-1] = item
                        break
                    if is_skip:
                        break
                if is_skip:
                    continue
                break

            self.__current = item
            self.__idx += 1
            self.__memo_hash = None
            return item
            }
        }
    
    private:
        struct STreeIterator
        {
            TObject* it;
            STreeIterator* parent;
            size_t command;

            STreeIterator(TObject* _it = NULL,
                          STreeIterator* _parent = NULL,
                          size_t _command = 0)
                : it(_it), parent(_parent), command(_command) {}
        }

        int _idx;
        TObject* _obj;
        STreeIterator* _it;
        void* _parent;
    };
}

#endif // __LAZY_ITERATOR_H__