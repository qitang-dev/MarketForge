#include "../../include/indicator/volatility.hpp"

#include <cmath>
#include <cstddef>
#include <stdexcept>

#include "../../include/data/constant.hpp"
#include "../../include/data/data_utils.hpp"

double calculate_stddev(const TimeSeries& values,
                        std::size_t window,
                        std::size_t end_index) {
  if (window == 0 || end_index >= values.size()) {
    throw std::invalid_argument("Invalid standard deviation parameters.");
  }

  if (end_index + 1 < window) {
    throw std::invalid_argument("Not enough data.");
  }

  const std::size_t start_index = end_index - window + 1;

  double window_sum = 0.0;
  for (std::size_t i = start_index; i <= end_index; ++i) {
    if (std::isnan(values[i].value)) {
      return NaN;
    }
    window_sum += values[i].value;
  }
  const double window_mean = window_sum / static_cast<double>(window);

  double squared_diff_sum = 0.0;
  for (std::size_t i = start_index; i <= end_index; ++i) {
    const double diff = values[i].value - window_mean;
    squared_diff_sum += diff * diff;
  }
  // using population variance here (ddof = n)
  const double variance = squared_diff_sum / static_cast<double>(window);

  return std::sqrt(variance);
}