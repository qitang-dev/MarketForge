#pragma once

#include <string>

#include "market_snapshot.hpp"
#include "price_bar.hpp"
#include "time_series.hpp"

class DataLoader {
 public:
  DataLoader() = default;
  explicit DataLoader(char delimiter);
  PriceFrame load_csv(const std::string& filename) const;

 private:
  char delimiter_{','};
};