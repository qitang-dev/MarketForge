#include "../../include/strategy/rsi_strategy.hpp"

#include <stdexcept>

#include "../../include/data/data_utils.hpp"
#include "../../include/indicator/moving_average.hpp"
#include "../../include/indicator/rsi.hpp"
#include "../../include/indicator/volatility.hpp"

RSIStrategy::RSIStrategy(std::size_t window,
                         double oversold_threshold,
                         double overbought_threshold,
                         double PriceBar::* price_type)
    : window_(window),
      oversold_threshold_(oversold_threshold),
      overbought_threshold_(overbought_threshold),
      price_type_(price_type) {
  if (window_ == 0) {
    throw std::invalid_argument("Window must be greater than 0.");
  }
  if (overbought_threshold_ < 0.0 || overbought_threshold_ > 100.0 ||
      oversold_threshold_ < 0.0 || oversold_threshold_ > 100.0 ||
      oversold_threshold_ >= overbought_threshold_) {
    throw std::invalid_argument("Invalid RSI thresholds.");
  }
}

Signal RSIStrategy::generate_signal(
    std::span<const PriceBar> price_history) const {
  if (price_history.size() < window_ + 2) {
    return Signal{.type = SignalType::HOLD};
  }
  const std::size_t today_end_index = price_history.size() - 1;
  const std::size_t yesterday_end_index = price_history.size() - 2;
  const TimeSeries close_prices =
      extract_price_series(price_history, price_type_);

  const double rsi_today =
      calculate_rsi(close_prices, window_, today_end_index);

  const double rsi_yesterday =
      calculate_rsi(close_prices, window_, yesterday_end_index);

  if (rsi_yesterday < oversold_threshold_ && rsi_today >= oversold_threshold_) {
    return Signal{.type = SignalType::BUY};
  }
  if (rsi_yesterday > overbought_threshold_ &&
      rsi_today <= overbought_threshold_) {
    return Signal{.type = SignalType::SELL};
  }
  return Signal{.type = SignalType::HOLD};
}

std::string RSIStrategy::name() const { return "RSI"; }
std::string RSIStrategy::parameters() const {
  return "window=" + std::to_string(window_) +
         ", oversold=" + std::to_string(oversold_threshold_) +
         ", overbought=" + std::to_string(overbought_threshold_);
}