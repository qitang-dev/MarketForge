#pragma once

#include "../market/market_snapshot.hpp"
#include "signal.hpp"

class Strategy {
 public:
  virtual ~Strategy() = default;

  virtual Signal generate_signal(const MarketSnapShot& previous,
                                 const MarketSnapShot& current) = 0;
};