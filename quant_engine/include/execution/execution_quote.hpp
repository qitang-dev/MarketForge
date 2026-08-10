#pragma once

struct ExecutionQuote {
  double execution_price{0.0};
  int quantity{0};
  double trade_value{0.0};
  double commission{0.0};
  double stamp_duty{0.0};
  double slippage_cost{0.0};
  double total_fee{0.0};
};