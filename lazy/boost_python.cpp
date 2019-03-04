
#include "bind_python.h"

#define BOOST_PYTHON_STATIC_LIB

BOOST_PYTHON_MODULE(HelloExt)
{
    using namespace boost::python;
    class_<Lazy::TIterator>("Iterator")
        .def("next", &Lazy::TIterator::next)
        ;
}