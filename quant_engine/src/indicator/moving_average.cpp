#include "../../include/indicator/moving_average.hpp"

#include <cmath>
#include <stdexcept>

#include "../../include/data/data_utils.hpp"

double calculate_sma(const TimeSeries& prices,
                     std::size_t window,
                     std::size_t end_index) {
  if (window == 0 || end_index >= prices.size()) {
    throw std::invalid_argument("Invalid SMA parameters.");
  }

  if (end_index + 1 < window) {
    throw std::invalid_argument("Not enough data for SMA.");
  }
  std::size_t start_index = end_index - window + 1;
  double window_sum{0.0};
  for (std::size_t i = start_index; i < end_index + 1; ++i) {
    window_sum += prices.at(i).value;
  }
  return window_sum / static_cast<double>(window);
}

TimeSeries simple_moving_average(const TimeSeries& prices,
                                 std::size_t time_period) {
  if (time_period <= 1) {
    throw std::invalid_argument("Time period must be greater than 1.");
  }

  const TimeSeries kCleanPrices = drop_nan(prices);
  const std::size_t kCleanLength = kCleanPrices.size();

  if (kCleanLength == 0) {
    throw std::invalid_argument(
        "The length of valid prices must greater than 0.");
  }
  if (kCleanLength < time_period) {
    throw std::invalid_argument(
        "The time period must not be greater than the number of valid prices.");
  }

  TimeSeries results;
  results.reserve(kCleanLength - time_period + 1);

  double rolling_sum = 0.0;
  for (std::size_t i = 0; i < time_period; ++i) {
    rolling_sum += kCleanPrices[i].value;
  }

  for (std::size_t j = 0; j < (kCleanLength - time_period + 1); ++j) {
    const std::size_t kEndWindowIndex = (j + time_period - 1);

    if (j > 0) {
      rolling_sum = rolling_sum - kCleanPrices[j - 1].value +
                    kCleanPrices[kEndWindowIndex].value;
    }

    const double kRollingMean = rolling_sum / static_cast<double>(time_period);
    const std::string& kDate = kCleanPrices[kEndWindowIndex].timestamp;
    results.push_back(TimeSeriesPoint{kDate, kRollingMean});
  }

  return results;
}

TimeSeries exp_moving_average(const TimeSeries& prices,
                              std::size_t time_period) {
  if (time_period == 0) {
    throw std::invalid_argument("Time period must be greater than 1.");
  }

  const TimeSeries kCleanPrices = drop_nan(prices);
  const std::size_t kCleanLength = kCleanPrices.size();

  if (kCleanPrices.empty()) {
    throw std::invalid_argument(
        "The length of valid prices must greater than 0.");
  }

  const double kAlpha = 2.0 / static_cast<double>(time_period + 1);
  TimeSeries results;
  results.reserve(kCleanLength);
  results.push_back(kCleanPrices.front());

  for (std::size_t i = 1; i < kCleanLength; ++i) {
    double current_ema =
        (kAlpha * kCleanPrices[i].value + (1 - kAlpha) * results.back().value);
    results.push_back(TimeSeriesPoint{kCleanPrices[i].timestamp, current_ema});
  }

  return results;
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

TimeSeries rolling_max(TimeSeries values, std::size_t time_period) {
  if (time_period <= 1) {
    throw std::invalid_argument("Time period must be greater than 1.");
  }
  const TimeSeries kCleanValue = drop_nan(values);
  const std::size_t kCleanLength = kCleanValue.size();

  if (kCleanValue.empty()) {
    throw std::invalid_argument(
        "The length of valid values must greater than 0.");
  }
  if (kCleanLength < time_period) {
    throw std::invalid_argument(
        "The time period must not be greater than the number of valid prices.");
  }

  TimeSeries results;
  results.reserve(kCleanLength - time_period + 1);

  double rolling_max = kCleanValue.front().value;
  for (std::size_t i = 0; i < time_period; ++i) {
    rolling_max = std::max(kCleanValue[i].value, rolling_max);
  }

  for (std::size_t j = 0; j < kCleanLength - time_period + 1; ++j) {
    if (j > 0) {
      rolling_max =
          std::max(kCleanValue[j + time_period - 1].value, rolling_max);
    }

    results.push_back(TimeSeriesPoint{
        kCleanValue[j + time_period - 1].timestamp, rolling_max});
  }
  return results;
}

TimeSeries rolling_min(TimeSeries values, std::size_t time_period) {
  if (time_period <= 1) {
    throw std::invalid_argument("Time period must be greater than 1.");
  }
  const TimeSeries kCleanValue = drop_nan(values);
  const std::size_t kCleanLength = kCleanValue.size();

  if (kCleanValue.empty()) {
    throw std::invalid_argument(
        "The length of valid values must greater than 0.");
  }
  if (kCleanLength < time_period) {
    throw std::invalid_argument(
        "The time period must not be greater than the number of valid prices.");
  }

  TimeSeries results;
  results.reserve(kCleanLength - time_period + 1);

  double rolling_min = kCleanValue.front().value;
  for (std::size_t i = 0; i < time_period; ++i) {
    rolling_min = std::min(kCleanValue[i].value, rolling_min);
  }

  for (std::size_t j = 0; j < kCleanLength - time_period + 1; ++j) {
    if (j > 0) {
      rolling_min =
          std::min(kCleanValue[j + time_period - 1].value, rolling_min);
    }

    results.push_back(TimeSeriesPoint{
        kCleanValue[j + time_period - 1].timestamp, rolling_min});
  }
  return results;
}