#pragma once

#ifndef __LAZY_DEFINES_H__
#define __LAZY_DEFINES_H__

#include <assert.h>

#include <list>
#include <tuple>

template<typename A, typename B>
using Tuple = std::tuple<A, B>;

template<typename A>
using List = std::list<A>;

#define _ass(s) assert(s)

#endif // __LAZY_DEFINES_H__