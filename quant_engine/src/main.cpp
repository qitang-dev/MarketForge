#include <iostream>

#include "../include/core/backtest_config.hpp"
#include "../include/core/order.hpp"
#include "../include/core/portfolio.hpp"
#include "../include/core/trade.hpp"
#include "../include/core/transaction_cost.hpp"
#include "../include/execution/execution_engine.hpp"
#include "../include/execution/execution_model.hpp"
#include "../include/execution/full_position_sizer.hpp"
#include "../include/execution/order_manager.hpp"
#include "../include/execution/order_validator.hpp"
#include "../include/strategy/moving_average_strategy.hpp"

int main() {
  Portfolio portfolio;
  portfolio.cash = 100000;

  std::cout << "Account Cash: " << portfolio.cash << '\n'
            << "Market Value: " << portfolio.market_value << '\n'
            << "Equity: " << portfolio.equity << '\n'
            << "Shares: " << portfolio.shares << '\n';

  MovingAverageStrategy strategy;

  MarketSnapShot previous = {"2026-08-09", "sh0001", 10.0, 9.0, 10.0};
  MarketSnapShot current = {"2026-08-09", "sh0001", 10.0, 12.0, 11.0};
  double market_price = current.close;

  Signal signal = strategy.generate_signal(previous, current);

  FullPositionSizer sizer;

  OrderManager manager;
  std::optional<Order> order =
      manager.generate_order(signal, portfolio, current, sizer);

  if (order) {
    std::cout << "\nOriginal Order\n"
              << "Order Symbol: " << order->symbol << '\n'
              << "Order Timestamp: " << order->timestamp << '\n'
              << "Order Side: " << to_string(order->side) << '\n'
              << "Order Quantity: " << order->quantity << '\n';
    BacktestConfig config;
    TransactionCostModel cost_model(config);
    ExecutionModel execution_model(cost_model);
    OrderValidator order_validator(execution_model);
    std::optional<Order> adjusted_order =
        order_validator.validate_order(*order, portfolio, market_price);

    std::cout << "\nAdjusted Order\n"
              << "Order Symbol: " << adjusted_order->symbol << '\n'
              << "Order Timestamp: " << adjusted_order->timestamp << '\n'
              << "Order Side: " << to_string(adjusted_order->side) << '\n'
              << "Order Quantity: " << adjusted_order->quantity << '\n';

    ExecutionEngine execution(execution_model);

    Trade trade = execution.execute(*adjusted_order, current.close);
    std::cout << "\nTrade Symbol: " << trade.symbol << '\n'
              << "Trade Time: " << trade.timestamp << '\n'
              << "Trade Type: " << to_string(trade.side) << '\n'
              << "Execution Price: " << trade.execution_price << '\n'
              << "Execution Quantity: " << trade.quantity << '\n'
              << "Commission: " << trade.commission << '\n'
              << "Stamp Duty: " << trade.stamp_duty << '\n'
              << "Slippage Cost: " << trade.slippage_cost << '\n';

    portfolio.apply_trade(trade);
    portfolio.update_market_value(market_price);
    std::cout << "\nAccount Cash: " << portfolio.cash << '\n'
              << "Market Value: " << portfolio.market_value << '\n'
              << "Equity: " << portfolio.equity << '\n'
              << "Shares: " << portfolio.shares << '\n';
  } else {
    std::cout << "No orders and trades generated." << '\n';
  }
  return 0;
}