#pragma once

#include "../../include/data/backtest_result.hpp"
#include "../../include/data/market_data.hpp"
#include "../../include/strategy/strategy.hpp"

BacktestSummary run_backtest(const std::string& symbol,
                             TimeFrame timeframe,
                             const PriceFrame& price_history,
                             std::size_t periods_per_year,
                             Strategy& strategy);