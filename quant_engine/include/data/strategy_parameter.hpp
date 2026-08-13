#pragma once

#include <cstddef>

#include "constant.hpp"

struct MAParams {
  std::size_t short_window{0};
  std::size_t long_window{0};
};

struct BollingerParams {
  std::size_t window{0};
  double num_std_dev{NaN};
};

struct RSIParams {
  std::size_t window{0};
  double oversold_threshold{NaN};
  double overbought_threshold{NaN};
};
