#pragma once

#ifndef __LAZY_DEFINES_PYTHON_H__
#define __LAZY_DEFINES_PYTHON_H__

#define BOOST_PYTHON_STATIC_LIB
#include <boost/python.hpp>

#include <assert.h>

#include <list>
#include <vector>
#include <tuple>
#include <memory>
#include <exception>

template<typename A, typename B>
using Tuple = std::tuple<A, B>;

template<typename A>
using List = std::list<A>;

template<typename A>
using Vector = std::vector<A>;

template<typename A>
using SharedPtr = std::shared_ptr<A>;
template<typename A>
using SharedPtrCRef = const std::shared_ptr<A>&;

template<typename A>
using SharedPtrSpec = boost::python::handle<A>;
template<typename A>
using SharedPtrSpecCRef = const boost::python::handle<A>&;

#define _ass(s) assert(s)

typedef std::exception Exception;

#endif // __LAZY_DEFINES_PYTHON_H__