#include "bind_cpp.h"

#include <iostream>
#include <time.h>

typedef Lazy::Iterator<Vector<int>, Lazy::SIter, Vector<int>::iterator> TVecIterator;

int main()
{
    SharedPtrSpec<Vector<int> > vec(new Vector<int>({1, 2, 3, 4, 5}));
    TVecIterator::TCommandPtr pCmd(new TVecIterator::TCommand());
    TVecIterator* it = new TVecIterator(vec);
    it->add(pCmd);
    for (int i = 0; i < 5; ++i)
        std::cout << **(it->next());
    std::cout << std::endl;
    it->reset();
    Vector<int> dummy;
    dummy.reserve(5000);
    time_t temp = clock();
    for (int j = 0; j < 1000; ++j)
    {
        for (int i = 0; i < 5; ++i)
            dummy.push_back(**(it->next()));
        it->reset();
    }
    std::cout << "CLOCKS_PER_SEC: " << CLOCKS_PER_SEC << std::endl;
    std::cout << "Clocks spent: " << (clock() - temp);
    delete it;
    return 0;
}