#pragma once
#include <iomanip>
#include <iostream>

#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_parameter_sensitivity(
    const std::pair<BacktestSummary, BacktestSummary>& sensitivity) {
  std::cout << std::fixed << std::setprecision(2);

  std::cout << "\n==========" << sensitivity.first.strategy_name
            << "==========\n";

  std::cout << "Best Performance Parameter Set: "
            << sensitivity.first.parameters << '\n';

  std::cout << "Symbol:              " << sensitivity.first.symbol << '\n';

  std::cout << "Timeframe:           " << to_string(sensitivity.first.timeframe)
            << '\n';

  std::cout << "--------------------------------------\n";

  std::cout << "Total Return:        " << sensitivity.first.total_return * 100.0
            << "%\n";

  std::cout << "Annualized Return:   "
            << sensitivity.first.annualized_return * 100.0 << "%\n";

  std::cout << "Annualized Volatility: "
            << sensitivity.first.annualized_volatility * 100.0 << "%\n";

  std::cout << "Max Drawdown:        " << sensitivity.first.max_drawdown * 100.0
            << "%\n";

  std::cout << "Sharpe Ratio:        " << sensitivity.first.sharpe_ratio
            << '\n';

  std::cout << "Sortino Ratio:       " << sensitivity.first.sortino_ratio
            << '\n';

  std::cout << "Calmar Ratio:        " << sensitivity.first.calmar_ratio
            << '\n';

  std::cout << "Closed Trades:       " << sensitivity.first.closed_trades
            << '\n';

  std::cout << "Win Rate:            " << sensitivity.first.win_rate * 100.0
            << "%\n";

  std::cout << "Profit-Loss Ratio:   " << sensitivity.first.profit_loss_ratio
            << '\n';

  std::cout << "======================================\n";

  std::cout << "Second Best Performance Parameter Set: "
            << sensitivity.first.parameters << '\n';

  std::cout << "Symbol:              " << sensitivity.second.symbol << '\n';

  std::cout << "Timeframe:           "
            << to_string(sensitivity.second.timeframe) << '\n';

  std::cout << "--------------------------------------\n";

  std::cout << "Total Return:        "
            << sensitivity.second.total_return * 100.0 << "%\n";

  std::cout << "Annualized Return:   "
            << sensitivity.second.annualized_return * 100.0 << "%\n";

  std::cout << "Annualized Volatility: "
            << sensitivity.second.annualized_volatility * 100.0 << "%\n";

  std::cout << "Max Drawdown:        "
            << sensitivity.second.max_drawdown * 100.0 << "%\n";

  std::cout << "Sharpe Ratio:        " << sensitivity.second.sharpe_ratio
            << '\n';

  std::cout << "Sortino Ratio:       " << sensitivity.second.sortino_ratio
            << '\n';

  std::cout << "Calmar Ratio:        " << sensitivity.second.calmar_ratio
            << '\n';

  std::cout << "Closed Trades:       " << sensitivity.second.closed_trades
            << '\n';

  std::cout << "Win Rate:            " << sensitivity.second.win_rate * 100.0
            << "%\n";

  std::cout << "Profit-Loss Ratio:   " << sensitivity.second.profit_loss_ratio
            << '\n';

  std::cout << "======================================\n";
}