
#include "bind_cpp.h"

#include <iostream>

int main()
{
    Vector<int> vec = {1, 2 , 3, 4, 5};
    Lazy::Iterator<Vector<int>, Vector<int>::iterator, int> it(SharedPtrSpec<Vector<int> >(&vec));
    typename TVecIterator::TCommandPtr cmd(new TVecIterator::TCommand());
    it.add(cmd);
    for (int i = 0; i < 5; ++i)
        std::cout << *(it.next());
    return 0;
}