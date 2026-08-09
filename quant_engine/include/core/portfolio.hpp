#pragma once

#include <stdexcept>
#include <string>

#include "order.hpp"
#include "trade.hpp"

struct Portfolio {
  double cash{0.0};
  int shares{0};
  double market_value{0.0};
  double equity{0.0};

  void update_market_value(double price) {
    market_value = shares * price;
    equity = cash + market_value;
  }

  void apply_trade(const Trade& trade) {
    double trade_value = trade.quantity * trade.execution_price;

    if (trade.side == OrderSide::BUY) {
      shares += trade.quantity;
      cash -= trade_value;
    } else if (trade.side == OrderSide::SELL) {
      if (trade.quantity > shares) {
        throw std::runtime_error("Insufficient Shares");
      }
      shares -= trade.quantity;
      cash += trade_value;
    }
    cash -= trade.commission;
    cash -= trade.stamp_duty;
  }
};