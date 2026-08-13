#include "../../include/backtest/run_backtest.hpp"

#include <stdexcept>

#include "../../include/backtest/backtester.hpp"
#include "../../include/core/backtest_config.hpp"
#include "../../include/core/order.hpp"
#include "../../include/core/portfolio.hpp"
#include "../../include/core/trade.hpp"
#include "../../include/core/transaction_cost.hpp"
#include "../../include/execution/execution_engine.hpp"
#include "../../include/execution/execution_model.hpp"
#include "../../include/execution/full_position_sizer.hpp"
#include "../../include/execution/order_manager.hpp"
#include "../../include/execution/order_validator.hpp"
#include "../../include/performance/performance_analyzer.hpp"

BacktestSummary run_backtest(
    const std::string& symbol,
    TimeFrame timeframe,
    const PriceFrame& price_history,
    std::size_t periods_per_year,
    Strategy& strategy
) {
  Portfolio portfolio;
  portfolio.cash = 100000;

  FullPositionSizer sizer;
  OrderManager manager;
  BacktestConfig config;
  TransactionCostModel cost_model(config);
  ExecutionModel execution_model(cost_model);
  OrderValidator order_validator(execution_model);
  ExecutionEngine execution(execution_model);

  Backtester backtester(strategy, sizer, manager, order_validator, execution, portfolio);

  BacktestResult result = backtester.run(symbol, price_history);
  ClosedTradeHistory closed_trades = PerformanceAnalyzer::extract_closed_trades(result);

  const double total_return = PerformanceAnalyzer::total_return(result);

  const double annualized_return = PerformanceAnalyzer::annualized_return(result, periods_per_year);

  const double annualized_volatility =
      PerformanceAnalyzer::annualized_volatility(result, periods_per_year);

  const double sharpe_ratio = PerformanceAnalyzer::sharpe_ratio(result, 0.0, periods_per_year);

  const double max_drawdown = PerformanceAnalyzer::max_drawdown(result);

  const double sortino_ratio = PerformanceAnalyzer::sortino_ratio(result, 0.0, periods_per_year);

  const double calmar_ratio = PerformanceAnalyzer::calmar_ratio(result, periods_per_year);

  const double win_rate = PerformanceAnalyzer::win_rate(closed_trades);

  const double profit_loss_ratio = PerformanceAnalyzer::profit_loss_ratio(closed_trades);

  return BacktestSummary{
      .symbol = symbol,
      .timeframe = timeframe,
      .strategy_name = strategy.name(),
      .parameters = strategy.parameters(),
      .total_return = total_return,
      .annualized_return = annualized_return,
      .annualized_volatility = annualized_volatility,
      .sharpe_ratio = sharpe_ratio,
      .sortino_ratio = sortino_ratio,
      .calmar_ratio = calmar_ratio,
      .max_drawdown = max_drawdown,
      .closed_trades = closed_trades.size(),
      .win_rate = win_rate,
      .profit_loss_ratio = profit_loss_ratio,
  };
}

std::string get_str_time_scale(TimeFrame timeframe) {
  switch (timeframe) {
    case TimeFrame::DAY_1:
      return "daily";
    case TimeFrame::MIN_5:
      return "min5";
  }
  throw std::invalid_argument("Unsupported time frame.");
}

std::size_t get_periods_per_year(TimeFrame timeframe) {
  switch (timeframe) {
    case TimeFrame::DAY_1:
      return 252;
    case TimeFrame::MIN_5:
      return 252 * 48;
  }
  throw std::invalid_argument("Unsupported time frame.");
}
