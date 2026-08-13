#include "../../include/strategy/bollinger_strategy.hpp"

#include <stdexcept>

#include "../../include/data/data_utils.hpp"
#include "../../include/indicator/moving_average.hpp"
#include "../../include/indicator/volatility.hpp"

BollingerStrategy::BollingerStrategy(
    std::size_t window, double num_std_dev, double PriceBar::* price_type
)
    : window_(window), num_std_dev_(num_std_dev), price_type_(price_type) {
  if (window_ == 0) {
    throw std::invalid_argument("Window must be greater than 0.");
  }
}

Signal BollingerStrategy::generate_signal(std::span<const PriceBar> price_history) const {
  if (price_history.size() < window_ + 1) {
    return Signal{.type = SignalType::HOLD};
  }

  const std::size_t today_index = price_history.size() - 1;
  const std::size_t yesterday_index = price_history.size() - 2;

  const double sma_today = calculate_sma(price_history, window_, today_index, price_type_);
  const double sma_yesterday = calculate_sma(price_history, window_, yesterday_index, price_type_);

  const double stddev_today = calculate_stddev(price_history, window_, today_index, price_type_);
  const double stddev_yesterday =
      calculate_stddev(price_history, window_, yesterday_index, price_type_);

  const double upper_today = sma_today + num_std_dev_ * stddev_today;
  const double upper_yesterday = sma_yesterday + num_std_dev_ * stddev_yesterday;

  const double lower_today = sma_today - num_std_dev_ * stddev_today;
  const double lower_yesterday = sma_yesterday - num_std_dev_ * stddev_yesterday;

  if (price_history[yesterday_index].*price_type_ <= upper_yesterday &&
      price_history[today_index].*price_type_ > upper_today) {
    return Signal{.type = SignalType::BUY};
  }
  if (price_history[yesterday_index].*price_type_ >= lower_yesterday &&
      price_history[today_index].*price_type_ < lower_today) {
    return Signal{.type = SignalType::SELL};
  }
  return Signal{.type = SignalType::HOLD};
}

std::string BollingerStrategy::name() const { return "Bollinger"; }
std::string BollingerStrategy::parameters() const {
  return "window: " + std::to_string(window_) +
         ", std_dev_multiplier: " + std::to_string(num_std_dev_);
}