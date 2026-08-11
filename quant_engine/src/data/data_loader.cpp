#include "../../include/data/data_loader.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>

DataLoader::DataLoader(char delimiter) : delimiter_(delimiter) {}

PriceFrame DataLoader::load_csv(const std::string& filename) const {
  std::ifstream ifs(filename);

  if (!ifs.is_open()) {
    throw std::runtime_error("Cannot open the file:" + filename);
  }
  PriceFrame output;

  std::string line;
  // skip the header
  std::getline(ifs, line);

  while (std::getline(ifs, line)) {
    std::stringstream ss(line);

    std::string timestamp;
    std::string open;
    std::string high;
    std::string low;
    std::string close;
    std::string volume;
    std::string turnover;
    std::string amount;

    std::getline(ss, timestamp, delimiter_);
    std::getline(ss, open, delimiter_);
    std::getline(ss, high, delimiter_);
    std::getline(ss, low, delimiter_);
    std::getline(ss, close, delimiter_);
    std::getline(ss, volume, delimiter_);
    std::getline(ss, turnover, delimiter_);
    std::getline(ss, amount, delimiter_);

    output.push_back(PriceBar{
        .timestamp = timestamp,
        .open = std::stod(open),
        .close = std::stod(close),
        .high = std::stod(high),
        .low = std::stod(low),
        .volume = std::stod(volume),
        .turnover = std::stod(turnover),
        .amount = std::stod(amount),
    });
  }
  return output;
}