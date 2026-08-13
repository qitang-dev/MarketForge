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

TimeSeries rolling_volatility(TimeSeries returns, std::size_t time_period) {
  if (time_period <= 1) {
    throw std::invalid_argument("Time period must be greater than 1.");
  }
  const TimeSeries kCleanReturns = drop_nan(returns);
  const std::size_t kCleanLength = kCleanReturns.size();

  if (kCleanReturns.empty()) {
    throw std::invalid_argument(
        "The length of valid returns must greater than 0.");
  }
  if (kCleanLength < time_period) {
    throw std::invalid_argument(
        "The time period must not be greater than the number of valid prices.");
  }

  TimeSeries results;
  results.reserve(kCleanLength - time_period + 1);
  const double kTimePeriod = static_cast<double>(time_period);

  double rolling_sum = 0.0;
  double rolling_square_sum = 0.0;

  for (std::size_t i = 0; i < time_period; ++i) {
    rolling_sum += kCleanReturns[i].value;
    rolling_square_sum += kCleanReturns[i].value * kCleanReturns[i].value;
  }

  for (std::size_t j = 0; j < (kCleanLength - time_period + 1); ++j) {
    const std::size_t kEndWindowIndex = j + time_period - 1;

    if (j > 0) {
      rolling_sum = rolling_sum + kCleanReturns[kEndWindowIndex].value -
                    kCleanReturns[j - 1].value;

      rolling_square_sum =
          rolling_square_sum +
          (kCleanReturns[kEndWindowIndex].value *
           kCleanReturns[kEndWindowIndex].value) -
          (kCleanReturns[j - 1].value * kCleanReturns[j - 1].value);
    }

    const double kNumerator =
        rolling_square_sum - (rolling_sum * rolling_sum / kTimePeriod);
    const double kWindowVariance = kNumerator / (kTimePeriod - 1.0);

    const double kWindowVolatility = std::sqrt(kWindowVariance);

    results.push_back(TimeSeriesPoint{kCleanReturns[kEndWindowIndex].timestamp,
                                      kWindowVolatility});
  }

  return results;
}