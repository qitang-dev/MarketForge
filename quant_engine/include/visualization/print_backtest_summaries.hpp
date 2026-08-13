#pragma once

#include <iomanip>
#include <iostream>

#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_backtest_summary(std::ostream& os, const BacktestSummary& summary) {
  os << "========== Backtest Summary ==========\n";

  os << std::left << std::setw(24) << "Symbol:" << summary.symbol << '\n';

  os << std::left << std::setw(24) << "Timeframe:" << to_string(summary.timeframe) << '\n';

  os << std::left << std::setw(24) << "Strategy:" << summary.strategy_name << '\n';

  os << std::left << std::setw(24) << "Parameters:" << summary.parameters << '\n';

  os << "--------------------------------------\n";

  os << std::fixed << std::setprecision(2);

  os << std::left << std::setw(24) << "Total Return:" << summary.total_return * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Annualized Return:" << summary.annualized_return * 100.0
     << "%\n";

  os << std::left << std::setw(24)
     << "Annualized Volatility:" << summary.annualized_volatility * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Max Drawdown:" << summary.max_drawdown * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Sharpe Ratio:" << summary.sharpe_ratio << '\n';

  os << std::left << std::setw(24) << "Sortino Ratio:" << summary.sortino_ratio << '\n';

  os << std::left << std::setw(24) << "Calmar Ratio:" << summary.calmar_ratio << '\n';

  os << std::left << std::setw(24) << "Closed Trades:" << summary.closed_trades << '\n';

  os << std::left << std::setw(24) << "Win Rate:" << summary.win_rate * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Average Win:" << summary.average_win << '\n';

  os << std::left << std::setw(24) << "Average Loss:" << summary.average_loss << '\n';

  os << std::left << std::setw(24) << "Max Win:" << summary.max_win << '\n';

  os << std::left << std::setw(24) << "Max Loss:" << summary.max_loss << '\n';

  os << std::left << std::setw(24) << "Profit-Loss Ratio:" << summary.profit_loss_ratio << '\n';

  os << "======================================\n";
}