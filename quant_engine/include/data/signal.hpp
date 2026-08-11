#pragma once
#include <string>
#include <vector>

enum class SignalType { BUY, SELL, HOLD };

struct Signal {
  SignalType type{SignalType::HOLD};
};

struct SignalSeriresPoint {
  std::string timestamp{};
  Signal type{SignalType::HOLD};
};

using SignalSeries = std::vector<SignalSeriresPoint>;