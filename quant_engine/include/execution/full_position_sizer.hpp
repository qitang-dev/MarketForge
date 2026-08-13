#pragma once

#include "position_sizer.hpp"

class FullPositionSizer : public PositionSizer {
  int calculate_quantity(const Portfolio& portfolio, double price) const override;
};