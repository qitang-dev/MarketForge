#pragma once

#include <string>
#include <vector>

#include "order.hpp"

struct Trade {
  std::string timestamp{};
  std::string symbol{};

  OrderSide side{OrderSide::BUY};

  int quantity{0};

  double execution_price{0.0};
  double commission{0.0};
  double stamp_duty{0.0};
  double slippage_cost{0.0};
};

using TradeHistory = std::vector<Trade>;