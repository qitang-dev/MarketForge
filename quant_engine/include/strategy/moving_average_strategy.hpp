#pragma once

#include "strategy.hpp"

class MovingAverageStrategy : public Strategy {
 public:
  MovingAverageStrategy() = default;
  Signal generate_signal(const MarketSnapShot& previous,
                         const MarketSnapShot& current) override;
};