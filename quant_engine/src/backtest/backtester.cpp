#include "../../include/backtest/backtester.hpp"

#include <cstddef>
#include <iostream>
#include <optional>
Backtester::Backtester(Strategy& strategy,
                       PositionSizer& sizer,
                       OrderManager& order_manager,
                       OrderValidator& order_validator,
                       ExecutionEngine& execution_engine,
                       Portfolio& portfolio)
    : strategy_(strategy),
      sizer_(sizer),
      order_manager_(order_manager),
      order_validator_(order_validator),
      execution_engine_(execution_engine),
      portfolio_(portfolio) {}

BacktestResult Backtester::run(const std::string& symbol,
                               std::span<const PriceBar> price_history) {
  EquityHistory equity_history;
  TradeHistory trades;
  for (std::size_t i = 0; i < price_history.size(); ++i) {
    std::span<const PriceBar> rolling_history(price_history.data(), i + 1);

    Signal signal = strategy_.generate_signal(rolling_history);

    std::optional<Order> order = order_manager_.generate_order(
        symbol, signal, portfolio_, rolling_history[i], sizer_);

    if (order) {
      std::optional<Order> valid_order = order_validator_.validate_order(
          *order, portfolio_, rolling_history[i].close);
      if (valid_order) {
        Trade trade =
            execution_engine_.execute(*valid_order, rolling_history[i].close);

        trades.push_back(trade);
        portfolio_.apply_trade(trade);
        portfolio_.update_market_value(rolling_history[i].close);
      }
    }

    portfolio_.update_market_value(rolling_history[i].close);

    equity_history.push_back(
        EquityPoint{.timestamp = rolling_history[i].timestamp,
                    .shares = portfolio_.shares,
                    .cash = portfolio_.cash,
                    .market_value = portfolio_.market_value,
                    .equity = portfolio_.equity});
  }
  return BacktestResult{
      .equity_history = equity_history,
      .trade_history = trades,
  };
}