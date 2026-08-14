#pragma once

#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

#include "../data/backtest_result.hpp"
#include "print_backtest_summaries.hpp"
#include "print_equity_history.hpp"
#include "print_parameter_sensitivity.hpp"
#include "print_trade_history.hpp"

void write_strategy_report(
    const std::filesystem::path& summary_dir,
    const std::filesystem::path& sensitivity_dir,
    const std::filesystem::path& best_equity_history_dir,
    const std::filesystem::path& best_trade_history_dir,
    const std::string& summary_file_name,
    const std::string& equity_history_file_name,
    const std::string& trade_history_file_name,
    const std::vector<BacktestRun>& runs,
    const ParameterSensitivity& sensitivity,
    const std::vector<double>& buy_hold,
    const std::vector<double>& drawdowns
) {
  std::filesystem::create_directories(summary_dir);
  std::filesystem::create_directories(sensitivity_dir);
  std::filesystem::create_directories(best_equity_history_dir);
  std::filesystem::create_directories(best_trade_history_dir);

  const std::filesystem::path summary_path = summary_dir / summary_file_name;
  const std::filesystem::path sensitivity_path = sensitivity_dir / summary_file_name;

  const std::filesystem::path equity_history_path =
      best_equity_history_dir / equity_history_file_name;

  const std::filesystem::path trade_history_path = best_trade_history_dir / trade_history_file_name;

  std::ofstream summary_file(summary_path);
  std::ofstream sensitivity_file(sensitivity_path);
  std::ofstream equity_history_file(equity_history_path);
  std::ofstream trade_history_file(trade_history_path);

  if (!summary_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + summary_path.string());
  }

  if (!sensitivity_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + sensitivity_path.string());
  }

  if (!equity_history_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + equity_history_path.string());
  }

  if (!trade_history_file.is_open()) {
    throw std::runtime_error("Failed to open file: " + trade_history_path.string());
  }

  for (const auto& run : runs) {
    print_backtest_summary(summary_file, run.summary);
    summary_file << '\n';
  }

  print_parameter_sensitivity(sensitivity_file, sensitivity);

  print_equity_history(
      equity_history_file,
      sensitivity.best_history.equity_history,
      buy_hold,
      drawdowns
  );

  print_trade_history(trade_history_file, sensitivity.best_history.trade_history);
}