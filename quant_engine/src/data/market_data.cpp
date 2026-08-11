#include "../../include/data/market_data.hpp"

#include <stdexcept>
void MarketData::add_data(const std::string& symbol,
                          TimeFrame timeframe,
                          PriceFrame data) {
  market_data_[symbol][timeframe] = std::move(data);
}

const PriceFrame& MarketData::get_data(const std::string& symbol,
                                       TimeFrame timeframe) const {
  auto symbol_it = market_data_.find(symbol);
  if (symbol_it == market_data_.end()) {
    throw std::runtime_error("Symbol data not found: " + symbol);
  }

  auto timeframe_it = symbol_it->second.find(timeframe);
  if (timeframe_it == symbol_it->second.end()) {
    throw std::runtime_error("TimeFrame data not found.");
  }

  return timeframe_it->second;
}