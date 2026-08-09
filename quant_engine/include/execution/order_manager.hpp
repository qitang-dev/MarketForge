#pragma once

#include "../core/order.hpp"
#include "../core/portfolio.hpp"
#include "../market/market_snapshot.hpp"
#include "../strategy/signal.hpp"
#include "position_sizer.hpp"

class OrderManager {
 public:
  Order generate_order(const Signal& signal, const Portfolio& portfolio,
                       const MarketSnapShot& snapshot,
                       const PositionSizer& sizer);
};