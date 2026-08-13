#pragma once

#include <string>
#include <vector>

#include "../../include/data/backtest_result.hpp"
#include "../../include/data/market_data.hpp"
#include "../../include/strategy/strategy.hpp"

std::pair<BacktestSummary, BacktestSummary> analyze_parameter_sensitivity(
    const std::string& symbol_name,
    TimeFrame timeframe,
    const std::string& strategy_name,
    const std::vector<BacktestSummary>& summaries
);

ParameterSensitivity analyze_parameter_sensitivity(const std::vector<BacktestSummary>& summaries);
