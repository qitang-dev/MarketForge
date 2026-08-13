#pragma once

#include <span>
#include <string>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "../data/time_series.hpp"

class Strategy {
 public:
  virtual ~Strategy() = default;
  virtual Signal generate_signal(
      std::span<const PriceBar> price_history) const = 0;
  virtual std::string name() const = 0;
  virtual std::string parameters() const = 0;
};