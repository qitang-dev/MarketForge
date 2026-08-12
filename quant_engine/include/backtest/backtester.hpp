#pragma once

#include <string>

#include "../data/backtest_result.hpp"
#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "../data/time_series.hpp"
#include "../execution/execution_engine.hpp"
#include "../execution/execution_model.hpp"
#include "../execution/execution_quote.hpp"
#include "../execution/full_position_sizer.hpp"
#include "../execution/order_manager.hpp"
#include "../execution/order_validator.hpp"
#include "../strategy/moving_average_strategy.hpp"
#include "../strategy/strategy.hpp"

class Backtester {
 public:
  Backtester(Strategy& strategy,
             PositionSizer& sizer,
             OrderManager& order_manager,
             OrderValidator& order_validator,
             ExecutionEngine& execution_engine,
             Portfolio& portfolio);

  BacktestResult run(const std::string& symbol,
                     std::span<const PriceBar> price_history);

 private:
  Strategy& strategy_;
  PositionSizer& sizer_;
  OrderManager& order_manager_;
  OrderValidator& order_validator_;
  ExecutionEngine& execution_engine_;
  Portfolio& portfolio_;
};