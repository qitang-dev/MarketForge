#pragma once

#include <string>
#include <unordered_map>

#include "price_bar.hpp"

enum class TimeFrame { MIN_5, DAY_1 };

struct TimeFrameHash {
  std::size_t operator()(TimeFrame tf) const {
    return static_cast<std::size_t>(tf);
  }
};

using TimeFrameData = std::unordered_map<TimeFrame, PriceFrame, TimeFrameHash>;

class MarketData {
 public:
  void add_data(const std::string& symbol,
                TimeFrame timeframe,
                PriceFrame data);
  const PriceFrame& get_data(const std::string& symbol,
                             TimeFrame timeframe) const;

 private:
  std::unordered_map<std::string, TimeFrameData> market_data_;
};