#include <iostream>

#include "../include/core/backtest_config.hpp"
#include "../include/core/order.hpp"
#include "../include/core/portfolio.hpp"
#include "../include/core/trade.hpp"
#include "../include/core/transaction_cost.hpp"
#include "../include/execution/execution_engine.hpp"
#include "../include/execution/full_position_sizer.hpp"
#include "../include/execution/order_manager.hpp"
#include "../include/strategy/moving_average_strategy.hpp"

int main() {
  Portfolio portfolio;
  portfolio.cash = 100000;

  MovingAverageStrategy strategy;

  MarketSnapShot previous = {"2026-08-09", "sh0001", 10.0, 11.0, 10.0};
  MarketSnapShot current = {"2026-08-09", "sh0001", 10.0, 10.0, 11.0};

  Signal signal = strategy.generate_signal(previous, current);

  FullPositionSizer sizer;

  OrderManager manager;
  auto order = manager.generate_order(signal, portfolio, current, sizer);
  order->quantity = 1000;

  if (order) {
    std::cout << order->symbol << '\n'
              << order->timestamp << '\n'
              << to_string(order->side) << '\n'
              << order->quantity << '\n';
  }

  BacktestConfig config;
  auto cost_model = TransactionCostModel(config);
  auto execution = ExecutionEngine(cost_model);

  if (order) {
    Trade trade = execution.execute(*order, current.close);
    std::cout << trade.symbol << '\n'
              << trade.timestamp << '\n'
              << to_string(trade.side) << '\n'
              << trade.execution_price << '\n'
              << trade.quantity << '\n'
              << trade.commission << '\n'
              << trade.stamp_duty << '\n'
              << trade.slippage_cost << '\n';
  }
  return 0;
}