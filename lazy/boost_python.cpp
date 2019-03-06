
#include "bind_python.h"

BOOST_PYTHON_MODULE(Lazy)
{
    using namespace boost::python;
    using namespace Lazy;
    class_<TIterator>("Iterator")
        .def(init<optional<typename TIterator::TObject*, TIterator*> >())
        .def("parent", &TIterator::parent, return_value_policy<reference_existing_object>())
        .def("reset", &TIterator::reset, return_value_policy<reference_existing_object>())
        .def("clear", &TIterator::clear, return_value_policy<reference_existing_object>())
        .def("add", &TIterator::add, return_value_policy<reference_existing_object>())
        .def("__iter__", &TIterator::self, return_value_policy<reference_existing_object>())
        .def("next", &TIterator::next)
        .def("__next__", &TIterator::next);

    class_<TIterator::TCommand>("Command")
        .def("exec", &TIterator::TCommand::exec);
}