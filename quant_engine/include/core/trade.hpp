#pragma once

#include <string>
#include <vector>

#include "order.hpp"

struct Trade {
  std::string symbol{};
  std::string timestamp{};

  OrderSide side{OrderSide::BUY};

  int quantity{0};

  double execution_price{0.0};
  double commission{0.0};
  double stamp_duty{0.0};
  double slippage_cost{0.0};
};

using TradeHistory = std::vector<Trade>;

struct ClosedTrade {
  std::string symbol{};
  std::string entry_timestamp{};
  std::string exit_timestamp{};
  int quantity{0};
  double entry_price{0.0};
  double exit_price{0.0};
  double pnl;
  double return_rate{0.0};
};

using ClosedTradeHistory = std::vector<ClosedTrade>;