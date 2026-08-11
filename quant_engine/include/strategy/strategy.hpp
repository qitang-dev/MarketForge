#pragma once

#include <span>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "../data/time_series.hpp"

class Strategy {
 public:
  virtual ~Strategy() = default;
  virtual Signal generate_signal(
      std::span<const PriceBar> price_history) const = 0;
};