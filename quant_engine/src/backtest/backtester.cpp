#include "../../include/backtest/backtester.hpp"

#include <cstddef>
#include <iostream>
#include <optional>

Backtester::Backtester(
    Strategy& strategy,
    PositionSizer& sizer,
    OrderManager& order_manager,
    OrderValidator& order_validator,
    ExecutionEngine& execution_engine,
    Portfolio& portfolio
)
    : strategy_(strategy),
      sizer_(sizer),
      order_manager_(order_manager),
      order_validator_(order_validator),
      execution_engine_(execution_engine),
      portfolio_(portfolio) {}

BacktestResult Backtester::run(const std::string& symbol, std::span<const PriceBar> price_history) {
  EquityHistory equity_history;
  TradeHistory trades;

  std::optional<Signal> pending_signal;

  for (std::size_t i = 0; i < price_history.size(); ++i) {
    const PriceBar& current_bar = price_history[i];

    // Excute the signal generated at the previous bar's close.
    if (pending_signal) {
      std::optional<Order> order = order_manager_.generate_order(
          symbol,
          *pending_signal,
          portfolio_,
          current_bar,
          current_bar.open,
          sizer_
      );

      if (order) {
        std::optional<Order> valid_order =
            order_validator_.validate_order(*order, portfolio_, current_bar.open);
        if (valid_order) {
          Trade trade = execution_engine_.execute(*valid_order, current_bar.open);

          // std::cout << "Trade executed at: " << current_bar.timestamp << '\n';

          // std::cout << "Reference open price: " << current_bar.open << '\n';

          // std::cout << "Execution price: " << trade.execution_price << '\n';

          trades.push_back(trade);
          portfolio_.apply_trade(trade);
        }
      }
    }
    portfolio_.update_market_value(current_bar.close);

    equity_history.push_back(
        EquityPoint{
            .timestamp = current_bar.timestamp,
            .shares = portfolio_.shares,
            .cash = portfolio_.cash,
            .market_value = portfolio_.market_value,
            .equity = portfolio_.equity
        }
    );
    // Generate the signal after the current bar has closed.
    std::span<const PriceBar> rolling_history(price_history.data(), i + 1);
    pending_signal = strategy_.generate_signal(rolling_history);

    // if (pending_signal->type != SignalType::HOLD) {
    // std::cout << "Signal generated at: " << current_bar.timestamp << '\n';
    // }
  }
  return BacktestResult{
      .equity_history = equity_history,
      .trade_history = trades,
  };
}