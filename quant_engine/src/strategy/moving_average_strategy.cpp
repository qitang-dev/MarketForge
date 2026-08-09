#include "../../include/strategy/moving_average_strategy.hpp"

Signal MovingAverageStrategy::generate_signal(const MarketSnapShot& previous,
                                              const MarketSnapShot& current) {
  Signal signal;
  // Golden Cross
  if (previous.short_ma <= previous.long_ma &&
      current.short_ma > current.long_ma) {
    signal.type = SignalType::BUY;
    // Death Cross
  } else if (previous.short_ma >= previous.long_ma &&
             current.short_ma < current.long_ma) {
    signal.type = SignalType::SELL;
  } else {
    signal.type = SignalType::HOLD;
  }
  return signal;
}