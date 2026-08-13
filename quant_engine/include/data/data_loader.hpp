#pragma once

#include <string>
#include <vector>

#include "price_bar.hpp"
#include "time_series.hpp"

class DataLoader {
 public:
  DataLoader() = default;
  explicit DataLoader(char delimiter);
  PriceFrame load_csv(const std::string& filepath) const;

 private:
  static std::vector<std::string> split_line(const std::string& line, char delimiter);
  char delimiter_{','};
};