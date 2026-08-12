#include <iostream>

#include "../include/backtest/backtester.hpp"
#include "../include/core/backtest_config.hpp"
#include "../include/core/order.hpp"
#include "../include/core/portfolio.hpp"
#include "../include/core/trade.hpp"
#include "../include/core/transaction_cost.hpp"
#include "../include/data/data_loader.hpp"
#include "../include/data/market_data.hpp"
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
  DataLoader loader(',');
  PriceFrame test_data =
      loader.load_csv("data/day_1/cleaned_sh600231_daily_qfq_tx.csv");

  MarketData market_data;
  market_data.add_data("sh600231", TimeFrame::DAY_1, std::move(test_data));

  const PriceFrame& history =
      market_data.get_data("sh600231", TimeFrame::DAY_1);

  std::cout << history.size() << '\n';
  /*
  PriceFrame test_data{
      {"2026-01-01", "sh001", 20, 20, 20, 20, 1000},
      {"2026-01-02", "sh001", 18, 18, 18, 18, 1000},
      {"2026-01-03", "sh001", 16, 16, 16, 16, 1000},
      {"2026-01-04", "sh001", 14, 14, 14, 14, 1000},
      {"2026-01-05", "sh001", 12, 12, 12, 12, 1000},
      {"2026-01-06", "sh001", 14, 14, 14, 14, 1000},
      {"2026-01-07", "sh001", 17, 17, 17, 17, 1000},
      {"2026-01-08", "sh001", 20, 20, 20, 20, 1000},
      {"2026-01-09", "sh001", 23, 23, 23, 23, 1000},
      {"2026-01-10", "sh001", 26, 26, 26, 26, 1000},
  };
  */

  MovingAverageStrategy sma(3, 5);
  FullPositionSizer sizer;
  OrderManager manager;
  BacktestConfig config;
  TransactionCostModel cost_model(config);
  ExecutionModel execution_model(cost_model);
  OrderValidator order_validator(execution_model);
  ExecutionEngine execution(execution_model);

  Backtester backtester(
      sma, sizer, manager, order_validator, execution, portfolio);

  backtester.run("sh600231", history);

  /*
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
*/
}