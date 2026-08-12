#pragma once
#include <cstddef>

#include "../data/time_series.hpp"

double calculate_stddev(const TimeSeries& values,
                        std::size_t window,
                        std::size_t end_index);