#include "../../include/data/data_utils.hpp"

#include <cmath>

#include "../../include/data/constant.hpp"

namespace {
double mean_clean(const TimeSeries& kCleanValues) {
  double sum = 0.0;
  for (const auto& point : kCleanValues) {
    sum += point.value;
  }
  return sum / static_cast<double>(kCleanValues.size());
}

double var_clean(const TimeSeries& kCleanValues, std::size_t ddof) {
  const std::size_t n = kCleanValues.size();
  if (n <= ddof) return NaN;

  double total_diff_sq = 0.0;
  const double average = mean_clean(kCleanValues);
  for (const auto& point : kCleanValues) {
    double diff = point.value - average;
    total_diff_sq += diff * diff;
  }
  return total_diff_sq / static_cast<double>(n - ddof);
}

double max_clean(const TimeSeries& kCleanValues) {
  double current_max = kCleanValues.front().value;
  for (const auto& point : kCleanValues) {
    current_max = std::max(point.value, current_max);
  }
  return current_max;
}

double min_clean(const TimeSeries& kCleanValues) {
  double current_min = kCleanValues.front().value;
  for (const auto& point : kCleanValues) {
    current_min = std::min(point.value, current_min);
  }
  return current_min;
}
}  // namespace

TimeSeries drop_nan(const TimeSeries& series) {
  TimeSeries results;
  results.reserve(series.size());

  for (const auto& point : series) {
    if (!std::isnan(point.value)) {
      results.push_back(point);
    }
  }
  return results;
}

double mean(const TimeSeries& series) {
  const TimeSeries kCleanValues = drop_nan(series);
  if (kCleanValues.empty()) return NaN;
  return mean_clean(kCleanValues);
}

double var(const TimeSeries& series, std::size_t ddof) {
  const TimeSeries kCleanValues = drop_nan(series);
  return var_clean(kCleanValues, ddof);
}

double stdev(const TimeSeries& series, std::size_t ddof) {
  const TimeSeries kCleanValues = drop_nan(series);
  return std::sqrt(var_clean(kCleanValues, ddof));
}

double max(const TimeSeries& series) {
  const TimeSeries kCleanValues = drop_nan(series);
  return max_clean(kCleanValues);
}

double min(const TimeSeries& series) {
  const TimeSeries kCleanValues = drop_nan(series);
  return min_clean(kCleanValues);
}
