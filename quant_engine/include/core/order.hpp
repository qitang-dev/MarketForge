#pragma once

#include <string>

enum class OrderSide { BUY, SELL, HOLD };

struct Order {
  std::string timestamp{};
  std::string symbol{};
  OrderSide side{OrderSide::BUY};
  int quantity{0};
};

inline std::string to_string(OrderSide side) {
  switch (side) {
    case OrderSide::BUY:
      return "BUY";

    case OrderSide::SELL:
      return "SELL";

    case OrderSide::HOLD:
      return "HOLD";
  }
  return "UNKNOWN";
}
