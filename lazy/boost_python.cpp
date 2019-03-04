
#include "bind_python.h"

BOOST_PYTHON_MODULE(HelloExt)
{
    using namespace boost::python;
    class_<Lazy::TIterator>("Iterator")
        .def("next", &Lazy::TIterator::next)
        ;
}