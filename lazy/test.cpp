#include "bind_cpp.h"

#include <iostream>
#include <time.h>

typedef Lazy::InternalIterator<Lazy::IterableÑpp<Vector<int>, Lazy::SIter, Vector<int>::iterator>, Vector<int>, Lazy::SIter, Vector<int>::iterator> TVecIterator;

int main()
{
    TVecIterator::TCommandPtr pCmd(new TVecIterator::TCommand());
    TVecIterator* it = new TVecIterator(SharedPtrSpec<Vector<int> >(new Vector<int>({ 1, 2, 3, 4, 5 })));
    it->add(pCmd);
    while (true)
    {
        try
        {
            std::cout << **(it->next());
        }
        catch (...)
        {
            break;
        }
    }
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