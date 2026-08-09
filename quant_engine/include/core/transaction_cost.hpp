#pragma once

#include "backtest_config.hpp"
#include "order.hpp"

struct TransactionCostModel {
  double commission_rate{0.0};
  double stamp_duty_rate{0.0};
  double slippage_rate{0.0};

  TransactionCostModel(const BacktestConfig& config)
      : commission_rate(config.commission_rate),
        stamp_duty_rate(config.stamp_duty_rate),
        slippage_rate(config.slippage_rate) {}

  double calculate_commission(double trade_value) const {
    return trade_value * commission_rate;
  }

  double calculate_stamp_duty(double trade_value, OrderSide side) const {
    if (side == OrderSide::SELL) {
      return trade_value * stamp_duty_rate;
    }
    return 0.0;
  }

  double calculate_slippage(double trade_value) const {
    return trade_value * slippage_rate;
  }
};
