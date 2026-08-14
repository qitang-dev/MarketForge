#pragma once

#include <cstddef>
#include <iostream>
#include <stdexcept>

#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_equity_history(
    std::ostream& os,
    const EquityHistory& equity_history,
    const std::vector<double>& buy_hold,
    const std::vector<double>& drawdowns
) {
  if (equity_history.size() != buy_hold.size() || equity_history.size() != drawdowns.size()) {
    throw std::invalid_argument("History series sizes do not macth.");
  }

  os << "timestamp,shares,cash,market_value,equity,buy_hold_equity,drawdown\n";

  for (std::size_t i = 0; i < equity_history.size(); ++i) {
    const EquityPoint& point = equity_history[i];
    os << point.timestamp << ','

       << point.shares << ','

       << point.cash << ','

       << point.market_value << ','

       << point.equity << ','

       << buy_hold[i] << ','

       << drawdowns[i] << '\n';
  }
}