#include "../../include/indicator/rsi.hpp"

#include <cmath>
#include <cstddef>
#include <span>
#include <stdexcept>

#include "../../include/data/constant.hpp"
#include "../../include/data/data_utils.hpp"

double calculate_rsi(
    std::span<const PriceBar> values,
    std::size_t window,
    std::size_t end_index,
    double PriceBar::* price_type
) {
  if (window == 0 || end_index >= values.size()) {
    throw std::invalid_argument("Invalid RSI parameters.");
  }

  if (end_index < window) {
    throw std::invalid_argument("Not enough data.");
  }

  const std::size_t start_index = end_index - window + 1;

  double total_gain = 0.0;
  double total_loss = 0.0;

  for (std::size_t i = start_index; i <= end_index; ++i) {
    const double current = values[i].*price_type;

    const double previous = values[i - 1].*price_type;

    const double change = current - previous;

    if (change > 0.0) {
      total_gain += change;
    } else if (change < 0.0) {
      total_loss += -change;
    }
  }

  const double average_gain = total_gain / static_cast<double>(window);

  const double average_loss = total_loss / static_cast<double>(window);

  if (average_gain == 0.0 && average_loss == 0.0) {
    return 50.0;
  }

  if (average_loss == 0.0) {
    return 100.0;
  }

  const double rs = average_gain / average_loss;

  return 100.0 - 100.0 / (1.0 + rs);
}