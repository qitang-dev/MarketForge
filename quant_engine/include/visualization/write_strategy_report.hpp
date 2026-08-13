#pragma once

#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

#include "../data/backtest_result.hpp"
#include "print_backtest_summaries.hpp"
#include "print_parameter_sensitivity.hpp"

void write_strategy_report(
    const std::filesystem::path& summary_dir,
    const std::filesystem::path& sensitivity_dir,
    const std::string& file_name,
    const std::vector<BacktestSummary>& summaries,
    const ParameterSensitivity& sensitivity
) {
  std::filesystem::create_directories(summary_dir);
  std::filesystem::create_directories(sensitivity_dir);

  const std::filesystem::path summary_path = summary_dir / file_name;
  const std::filesystem::path sensitivity_path = sensitivity_dir / file_name;

  std::ofstream summary_file(summary_path);
  std::ofstream sensitivity_file(sensitivity_path);

  if (!summary_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + summary_path.string());
  }

  if (!sensitivity_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + sensitivity_path.string());
  }

  for (const auto& summary : summaries) {
    print_backtest_summary(summary_file, summary);
    summary_file << '\n';
  }

  print_parameter_sensitivity(sensitivity_file, sensitivity);
}