#pragma once

#include <string>
#include <vector>

struct TimeSeriesPoint {
  std::string timestamp;
  double value{0.0};
};

using TimeSeries = std::vector<TimeSeriesPoint>;