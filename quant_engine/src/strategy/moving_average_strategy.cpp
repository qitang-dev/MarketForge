#include "../../include/strategy/moving_average_strategy.hpp"

#include <stdexcept>

#include "../../include/data/data_utils.hpp"
#include "../../include/indicator/moving_average.hpp"
MovingAverageStrategy::MovingAverageStrategy(std::size_t short_window,
                                             std::size_t long_window,
                                             double PriceBar::* price_type)
    : short_window_(short_window),
      long_window_(long_window),
      price_type_(price_type) {
  if (short_window <= 1 || long_window <= 1) {
    throw std::invalid_argument(
        "Moving-average windows must be greater than 1.");
  }
  if (short_window >= long_window) {
    throw std::invalid_argument(
        "The short window cannot be greater than the long window.");
  }
  if (price_type_ == nullptr) {
    throw std::invalid_argument("Invalid price field.");
  }
}

Signal MovingAverageStrategy::generate_signal(
    std::span<const PriceBar> price_history) const {
  if (price_history.size() < long_window_ + 1) {
    return Signal{.type = SignalType::HOLD};
  }

  TimeSeries close_prices = extract_price_series(price_history, price_type_);

  double short_today =
      calculate_sma(close_prices, short_window_, close_prices.size() - 1);

  double long_today =
      calculate_sma(close_prices, long_window_, close_prices.size() - 1);

  double short_yesterday =
      calculate_sma(close_prices, short_window_, close_prices.size() - 2);

  double long_yesterday =
      calculate_sma(close_prices, long_window_, close_prices.size() - 2);

  if (short_yesterday <= long_yesterday && short_today > long_today) {
    return Signal{SignalType::BUY};
  }

  if (short_yesterday >= long_yesterday && short_today < long_today) {
    return Signal{SignalType::SELL};
  }

  return Signal{SignalType::HOLD};
}
