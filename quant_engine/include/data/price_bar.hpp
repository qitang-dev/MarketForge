#pragma once

#include <string>
#include <vector>

struct PriceBar {
  std::string timestamp{};
  std::string symbol{};
  double open{0.0};
  double close{0.0};
  double high{0.0};
  double low{0.0};
  double volume{0.0};
  double turnover{0.0};
  double amount{0.0};
};

using PriceFrame = std::vector<PriceBar>;