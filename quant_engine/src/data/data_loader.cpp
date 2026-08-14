#include "../../include/data/data_loader.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

DataLoader::DataLoader(char delimiter) : delimiter_(delimiter) {}

PriceFrame DataLoader::load_csv(const std::string& filepath) const {
  std::ifstream file(filepath);

  if (!file.is_open()) {
    throw std::runtime_error("Cannot open the file: " + filepath);
  }

  std::string line;

  if (!std::getline(file, line)) {
    throw std::runtime_error("CSV file is empty: " + filepath);
  }

  const std::vector<std::string> headers = split_line(line, delimiter_);

  // Build: column name -> index
  std::unordered_map<std::string, std::size_t> column_index;

  for (std::size_t i = 0; i < headers.size(); ++i) {
    column_index[headers[i]] = i;
  }

  // Detect timestamp column
  std::size_t timestamp_index = 0;

  if (column_index.contains("datetime")) {
    timestamp_index = column_index.at("datetime");
  } else if (column_index.contains("date")) {
    timestamp_index = column_index.at("date");
  } else {
    throw std::runtime_error("CSV must contain 'date' or 'datetime' column.");
  }

  // Validate required OHLCV columns
  const std::vector<std::string> required_columns{
      "open",
      "high",
      "low",
      "close",
      "volume",
  };

  for (const auto& column : required_columns) {
    if (!column_index.contains(column)) {
      throw std::runtime_error("Missing required column: " + column);
    }
  }

  PriceFrame price_frame;

  // Read data rows
  while (std::getline(file, line)) {
    if (line.empty()) {
      continue;
    }

    const std::vector<std::string> fields = split_line(line, delimiter_);

    PriceBar bar{
        .timestamp = fields.at(timestamp_index),

        .open = std::stod(fields.at(column_index.at("open"))),

        .high = std::stod(fields.at(column_index.at("high"))),

        .low = std::stod(fields.at(column_index.at("low"))),

        .close = std::stod(fields.at(column_index.at("close"))),

        .volume = std::stod(fields.at(column_index.at("volume"))),
    };

    price_frame.push_back(bar);
  }

  return price_frame;
}

std::vector<std::string> DataLoader::split_line(const std::string& line, char delimiter) {
  std::vector<std::string> fields;
  std::stringstream ss(line);
  std::string field;
  while (getline(ss, field, delimiter)) {
    fields.push_back(field);
  }
  return fields;
}
