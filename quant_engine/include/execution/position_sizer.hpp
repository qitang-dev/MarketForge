#pragma once

#include "../core/portfolio.hpp"

class PositionSizer {
 public:
  virtual ~PositionSizer() = default;
  virtual int calculate_quantity(const Portfolio& portfolio, double price) const = 0;
};