#pragma once

#include <cstddef>
#include <span>
#include <string>
#include <vector>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "../data/time_series.hpp"

double calculate_sma(
    std::span<const PriceBar> values,
    std::size_t window,
    std::size_t end_index,
    double PriceBar::* price_type
);
TimeSeries simple_moving_average(const TimeSeries& prices, std::size_t time_period = 5);
TimeSeries exp_moving_average(const TimeSeries& prices, std::size_t time_period = 20);
TimeSeries rolling_volatility(TimeSeries returns, std::size_t time_period = 20);
TimeSeries rolling_max(TimeSeries values, std::size_t time_period = 5);
TimeSeries rolling_min(TimeSeries values, std::size_t time_period = 5);