#pragma once

#ifndef __LAZY_COMMANDS_H__
#define __LAZY_COMMANDS_H__

#include "defines.h"

namespace Lazy
{
    template<typename TValue, typename TBuffer>
    class Command
    {
    public:
        enum ECommandRet
        {
            eDone,
            eSkip,
            eList,
            eRepeat,
            eNotChanged
        };

        typedef Tuple<TValue*, ECommandRet> TRetTuple;

        Command() {};

        int id() const { return reinterpret_cast<int>(*this); }
        virtual TRetTuple exec(TValue* val, bool done, TBuffer* buffer, int idx) const
            { return TRetTuple(val, eDone); }
    };
}

#endif // __LAZY_COMMANDS_H__