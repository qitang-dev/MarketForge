#pragma once

#include <iomanip>
#include <iostream>

#include "../core/trade.hpp"
#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_trade_history(std::ostream& os, const TradeHistory& trade_history) {
  os << "timestamp,symbol,side,quantity,execution_price,"
        "commission,stamp_duty,slippage_cost\n";

  os << std::fixed << std::setprecision(6);

  for (const auto& trade : trade_history) {
    os << trade.timestamp << ','

       << trade.symbol << ','

       << to_string(trade.side) << ','

       << trade.quantity << ','

       << trade.execution_price << ','

       << trade.commission << ','

       << trade.stamp_duty << ','

       << trade.slippage_cost << '\n';
  }
}