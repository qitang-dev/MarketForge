#pragma once

#include "../strategy/bollinger_strategy.hpp"
#include "../strategy/moving_average_strategy.hpp"
#include "../strategy/rsi_strategy.hpp"

enum class StrategyType {
  MOVINGAVERGAE,
  BOLLINGER,
  RSI,
};
