#include "../../include/execution/full_position_sizer.hpp"

int FullPositionSizer::calculate_quantity(const Portfolio& portfolio, double price) const {
  int quantity = static_cast<int>(portfolio.cash / price);
  quantity = (quantity / 100) * 100;
  return quantity;
}