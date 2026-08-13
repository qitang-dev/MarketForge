#include "../../include/strategy/moving_average_strategy.hpp"

#include <stdexcept>

#include "../../include/data/data_utils.hpp"
#include "../../include/indicator/moving_average.hpp"
MovingAverageStrategy::MovingAverageStrategy(
    std::size_t short_window, std::size_t long_window, double PriceBar::* price_type
)
    : short_window_(short_window), long_window_(long_window), price_type_(price_type) {
  if (short_window_ <= 1 || long_window_ <= 1) {
    throw std::invalid_argument("Moving-average windows must be greater than 1.");
  }

  if (short_window_ >= long_window_) {
    throw std::invalid_argument("The short window cannot be greater than the long window.");
  }

  if (price_type_ == nullptr) {
    throw std::invalid_argument("Invalid price field.");
  }
}

Signal MovingAverageStrategy::generate_signal(std::span<const PriceBar> price_history) const {
  if (price_history.size() < long_window_ + 1) {
    return Signal{.type = SignalType::HOLD};
  }

  double short_today =
      calculate_sma(price_history, short_window_, price_history.size() - 1, price_type_);

  double long_today =
      calculate_sma(price_history, long_window_, price_history.size() - 1, price_type_);

  double short_yesterday =
      calculate_sma(price_history, short_window_, price_history.size() - 2, price_type_);

  double long_yesterday =
      calculate_sma(price_history, long_window_, price_history.size() - 2, price_type_);

  if (short_yesterday <= long_yesterday && short_today > long_today) {
    return Signal{SignalType::BUY};
  }

  if (short_yesterday >= long_yesterday && short_today < long_today) {
    return Signal{SignalType::SELL};
  }

  return Signal{SignalType::HOLD};
}

std::string MovingAverageStrategy::name() const { return "MovingAverage"; }
std::string MovingAverageStrategy::parameters() const {
  return "short=" + std::to_string(short_window_) + ", long=" + std::to_string(long_window_);
}