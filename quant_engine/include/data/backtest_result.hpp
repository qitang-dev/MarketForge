#pragma once

#include <string>
#include <vector>

#include "../core/trade.hpp"

struct EquityPoint {
  std::string timestamp{};
  int shares{0};
  double cash{0.0};
  double market_value{0.0};
  double equity{0.0};
};

using EquityHistory = std::vector<EquityPoint>;

struct BacktestResult {
  EquityHistory equity_history{};
  TradeHistory trade_history{};
};