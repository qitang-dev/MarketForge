#pragma once

struct BacktestConfig {
  double initial_capital{100000.0};
  double commission_rate{0.0005};
  double stamp_duty_rate{0.001};
  double slippage_rate{0.0005};

  bool validate() const {
    return commission_rate >= 0 && stamp_duty_rate >= 0 && slippage_rate >= 0;
  }
};