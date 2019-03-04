#include "bind_python.h"


char const* SayHello()
{
    return "Hello, from c++ dll!";
}

BOOST_PYTHON_MODULE(HelloExt)
{
    using namespace boost::python;
    def("SayHello", SayHello);
}