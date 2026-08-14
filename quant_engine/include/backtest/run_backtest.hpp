#pragma once

#include <cstddef>
#include <vector>

#include "../../include/data/backtest_result.hpp"
#include "../../include/data/market_data.hpp"
#include "../../include/strategy/strategy.hpp"

BacktestRun run_backtest(
    const std::string& symbol,
    TimeFrame timeframe,
    const PriceFrame& price_history,
    std::size_t periods_per_year,
    double initial_cash,
    Strategy& strategy
);

std::string get_str_time_scale(TimeFrame timeframe);

std::size_t get_periods_per_year(TimeFrame timeframe);

std::vector<double> calculate_drawdown_curve(const EquityHistory& history);

std::vector<double> calculate_buy_hold_curve(const PriceFrame& price_history, double initial_cash);