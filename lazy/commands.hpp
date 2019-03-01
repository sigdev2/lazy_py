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

        struct SCommandRet
        {
            SCommandRet(SharedPtrSpecCRef<TValue> _val, ECommandRet _code)
                : val(_val), code(_code) {};
            SharedPtrSpec<TValue> val;
            ECommandRet code;
        };
        
        struct SRetValue
        {
            SRetValue(SharedPtrSpecCRef<TValue> _val, bool _done)
                : val(_val), done(_done) {};
            SharedPtrSpec<TValue> val;
            bool done;
        };

        Command() {};

        virtual SCommandRet exec(SRetValue& val, TBuffer& buffer, int idx) const
        {
            return SCommandRet(val.val, (val.done ? eDone : eNotChanged));
        }
    };
}

#endif // __LAZY_COMMANDS_H__