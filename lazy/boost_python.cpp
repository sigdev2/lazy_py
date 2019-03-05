
#include "bind_python.h"

BOOST_PYTHON_MODULE(Lazy)
{
    using namespace boost::python;
    using namespace Lazy;
    class_<TInternalIterator>("InternalIterator")
        .def("parent", &TInternalIterator::parent, return_value_policy<reference_existing_object>())
        .def("reset", &TInternalIterator::reset, return_value_policy<reference_existing_object>())
        .def("clear", &TInternalIterator::clear, return_value_policy<reference_existing_object>())
        .def("add", &TInternalIterator::add, return_value_policy<reference_existing_object>())
        .def("next", &TInternalIterator::next)
        .def("__next__", &TInternalIterator::next);
}