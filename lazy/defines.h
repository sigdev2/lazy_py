#pragma once

#ifndef __LAZY_DEFINES_H__
#define __LAZY_DEFINES_H__

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
using SharedPtrSpec = std::shared_ptr<A>;
template<typename A>
using SharedPtrSpecCRef = const std::shared_ptr<A>&;

#define _ass(s) assert(s)

typedef std::exception Exception;

#endif // __LAZY_DEFINES_H__