#pragma once

#include <cstddef>
#include <string>
#include <vector>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "../data/time_series.hpp"

TimeSeries drop_nan(const TimeSeries& series);
double mean(const TimeSeries& series);
double var(const TimeSeries& series, std::size_t ddof = 1);
double stdev(const TimeSeries& series, std::size_t ddof = 1);
double max(const TimeSeries& series);
double min(const TimeSeries& series);

template <typename T>
TimeSeries extract_price_series(const T& df, double PriceBar::* price_type) {
  TimeSeries results;
  results.reserve(df.size());

  for (const auto& price_bar : df) {
    results.push_back(TimeSeriesPoint{price_bar.timestamp, price_bar.*price_type});
  }
  return results;
}