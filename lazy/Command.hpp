#pragma once

#ifndef __LAZY_COMMAND_H__
#define __LAZY_COMMAND_H__

namespace Lazy
{
    template<typename TValuePtr>
    class Command
    {
    public:
        typedef List<TValuePtr> TBuffer;
        
        typedef TValuePtr TValuePtr;

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
            SCommandRet(TValuePtr _val, ECommandRet _code)
                : val(_val), code(_code) {};
            TValuePtr val;
            ECommandRet code;
        };
        
        struct SRetValue
        {
            SRetValue(TValuePtr _val, bool _done)
                : val(_val), done(_done) {};
            TValuePtr val;
            bool done;
        };

        Command() {};

        virtual SCommandRet exec(SRetValue& val, TBuffer& buffer, int idx) const
        {
            return SCommandRet(val.val, (val.done ? eDone : eNotChanged));
        }
    };
}

#endif // __LAZY_COMMAND_H__