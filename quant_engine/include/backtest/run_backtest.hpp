#pragma once

#include <cstddef>

#include "../../include/data/backtest_result.hpp"
#include "../../include/data/market_data.hpp"
#include "../../include/strategy/strategy.hpp"

BacktestSummary run_backtest(
    const std::string& symbol,
    TimeFrame timeframe,
    const PriceFrame& price_history,
    std::size_t periods_per_year,
    Strategy& strategy
);

std::string get_str_time_scale(TimeFrame timeframe);

std::size_t get_periods_per_year(TimeFrame timeframe);