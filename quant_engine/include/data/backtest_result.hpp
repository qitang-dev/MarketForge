#pragma once

#include <cstddef>
#include <string>
#include <vector>

#include "../core/trade.hpp"
#include "../data/market_data.hpp"
#include "constant.hpp"

struct EquityPoint {
  std::string timestamp{};
  int shares{0};
  double cash{0.0};
  double market_value{0.0};
  double equity{0.0};
};

using EquityHistory = std::vector<EquityPoint>;

struct BacktestResult {
  EquityHistory equity_history{};
  TradeHistory trade_history{};
};

struct BacktestSummary {
  std::string symbol{};
  TimeFrame timeframe{};
  std::string strategy_name{};
  std::string parameters{};

  double total_return{NaN};
  double annualized_return{NaN};
  double annualized_volatility{NaN};
  double sharpe_ratio{NaN};
  double sortino_ratio{NaN};
  double calmar_ratio{NaN};
  double max_drawdown{NaN};

  std::size_t closed_trades{0};
  double win_rate{NaN};
  double average_win{NaN};
  double average_loss{NaN};
  double max_win{NaN};
  double max_loss{NaN};
  double profit_loss_ratio{NaN};
};

struct BacktestRun {
  BacktestSummary summary{};
  BacktestResult result{};
};

struct ParameterSensitivity {
  std::string symbol{};
  TimeFrame timeframe{};
  std::string strategy_name{};

  BacktestSummary best{};
  BacktestSummary second_best{};

  BacktestResult best_history{};

  double return_gap{0.0};
};