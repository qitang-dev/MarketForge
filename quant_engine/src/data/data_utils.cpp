#include "../../include/data/data_utils.hpp"

#include <cmath>

#include "../../include/data/constant.hpp"

namespace {
double mean_clean(const TimeSeries& clean_values) {
  double sum = 0.0;
  for (const auto& point : clean_values) {
    sum += point.value;
  }
  return sum / static_cast<double>(clean_values.size());
}

double var_clean(const TimeSeries& clean_values, std::size_t ddof) {
  const std::size_t n = clean_values.size();
  if (n <= ddof) return NaN;

  double total_diff_sq = 0.0;
  const double average = mean_clean(clean_values);
  for (const auto& point : clean_values) {
    double diff = point.value - average;
    total_diff_sq += diff * diff;
  }
  return total_diff_sq / static_cast<double>(n - ddof);
}

double max_clean(const TimeSeries& clean_values) {
  double current_max = clean_values.front().value;
  for (const auto& point : clean_values) {
    current_max = std::max(point.value, current_max);
  }
  return current_max;
}

double min_clean(const TimeSeries& clean_values) {
  double current_min = clean_values.front().value;
  for (const auto& point : clean_values) {
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
  const TimeSeries clean_values = drop_nan(series);
  if (clean_values.empty()) return NaN;
  return mean_clean(clean_values);
}

double var(const TimeSeries& series, std::size_t ddof) {
  const TimeSeries clean_values = drop_nan(series);
  return var_clean(clean_values, ddof);
}

double stdev(const TimeSeries& series, std::size_t ddof) {
  const TimeSeries clean_values = drop_nan(series);
  const double variance = var_clean(clean_values, ddof);
  if (std::isnan(variance)) {
    return NaN;
  }
  return std::sqrt(var_clean(clean_values, ddof));
}

double max(const TimeSeries& series) {
  const TimeSeries clean_values = drop_nan(series);
  if (clean_values.empty()) {
    return NaN;
  }
  return max_clean(clean_values);
}

double min(const TimeSeries& series) {
  const TimeSeries clean_values = drop_nan(series);
  if (clean_values.empty()) {
    return NaN;
  }
  return min_clean(clean_values);
}
