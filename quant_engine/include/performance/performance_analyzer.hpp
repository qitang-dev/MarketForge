#pragma once

#include <cstddef>

#include "../core/trade.hpp"
#include "../data/backtest_result.hpp"
#include "../data/data_utils.hpp"
#include "../data/time_series.hpp"

class PerformanceAnalyzer {
 public:
  static double total_return(const BacktestResult& result);
  static double annualized_return(const BacktestResult& result,
                                  std::size_t periods_per_year = 252);
  static double annualized_volatility(const BacktestResult& result,
                                      std::size_t periods_per_year = 252);
  static double sharpe_ratio(const BacktestResult& result,
                             double risk_free_rate = 0.0,
                             std::size_t periods_per_year = 252);
  static double max_drawdown(const BacktestResult& result);

  static double sortino_ratio(const BacktestResult& result,
                              double risk_free_rate = 0.0,
                              std::size_t periods_per_year = 252);

  static double calmar_ratio(const BacktestResult& result,
                             std::size_t periods_per_year = 252);

  static double average_win(const ClosedTradeHistory& closed_trades);

  static double average_loss(const ClosedTradeHistory& closed_trades);

  static double profit_loss_ratio(const ClosedTradeHistory& closed_trades);

  static double win_rate(const ClosedTradeHistory& closed_trades);

  static double max_win(const ClosedTradeHistory& closed_trades);

  static double max_loss(const ClosedTradeHistory& closed_trades);

    static ClosedTradeHistory extract_closed_trades(const BacktestResult& result);

 private:
  static TimeSeries extract_equity_curve(const BacktestResult& result);
  static TimeSeries simple_return(const TimeSeries& values);
  static TimeSeries drawdown(const TimeSeries& equity_curve);
};