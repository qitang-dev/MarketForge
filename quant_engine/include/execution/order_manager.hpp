#pragma once
#include <optional>

#include "../core/order.hpp"
#include "../core/portfolio.hpp"
#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "position_sizer.hpp"

class OrderManager {
 public:
  std::optional<Order> generate_order(const Signal& signal,
                                      const Portfolio& portfolio,
                                      const PriceBar& price_bar,
                                      const PositionSizer& sizer);
};