#pragma once

enum class SignalType { BUY, SELL, HOLD };

struct Signal {
  SignalType type{SignalType::HOLD};
};