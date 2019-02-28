
#include "bind_cpp.h"

#include <iostream>

int main()
{
    Vector<int> vec = {1, 2 , 3, 4, 5};
    TVecIterator it(SharedPtrSpec<Vector<int> >(&vec));
    TVecIterator::TCommandPtr cmd(new TVecIterator::TCommand());
    it.add(cmd);
    for (int i = 0; i < 5; ++i)
        std::cout << *(it.next());
    return 0;
}