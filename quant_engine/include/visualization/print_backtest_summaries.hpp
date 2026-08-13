#pragma once
#include <iomanip>
#include <iostream>

#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_backtest_summary(const BacktestSummary& summary) {
  std::cout << std::fixed << std::setprecision(2);

  std::cout << "\n========== Backtest Summary ==========\n";

  std::cout << "Symbol:              " << summary.symbol << '\n';

  std::cout << "Timeframe:           " << to_string(summary.timeframe) << '\n';

  std::cout << "Strategy:            " << summary.strategy_name << '\n';

  std::cout << "Parameters:          " << summary.parameters << '\n';

  std::cout << "--------------------------------------\n";

  std::cout << "Total Return:        " << summary.total_return * 100.0 << "%\n";

  std::cout << "Annualized Return:   " << summary.annualized_return * 100.0 << "%\n";

  std::cout << "Annualized Volatility: " << summary.annualized_volatility * 100.0 << "%\n";

  std::cout << "Max Drawdown:        " << summary.max_drawdown * 100.0 << "%\n";

  std::cout << "Sharpe Ratio:        " << summary.sharpe_ratio << '\n';

  std::cout << "Sortino Ratio:       " << summary.sortino_ratio << '\n';

  std::cout << "Calmar Ratio:        " << summary.calmar_ratio << '\n';

  std::cout << "Closed Trades:       " << summary.closed_trades << '\n';

  std::cout << "Win Rate:            " << summary.win_rate * 100.0 << "%\n";

  std::cout << "Profit-Loss Ratio:   " << summary.profit_loss_ratio << '\n';

  std::cout << "======================================\n";
}