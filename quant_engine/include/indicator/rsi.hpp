#pragma once
#include <cstddef>
#include <span>

#include "../data/price_bar.hpp"
#include "../data/time_series.hpp"

double calculate_rsi(
    std::span<const PriceBar> values,
    std::size_t window,
    std::size_t end_index,
    double PriceBar::* price_type
);