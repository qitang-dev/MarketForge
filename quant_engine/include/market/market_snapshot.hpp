#pragma once

#include <string>

struct MarketSnapShot {
  std::string timestamp;
  std::string symbol;
  double close{0.0};
  double short_ma{0.0};
  double long_ma{0.0};
};