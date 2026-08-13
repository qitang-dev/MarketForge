#include <iostream>
#include <vector>

#include "../include/backtest/backtester.hpp"
#include "../include/backtest/run_backtest.hpp"
#include "../include/core/backtest_config.hpp"
#include "../include/core/order.hpp"
#include "../include/core/portfolio.hpp"
#include "../include/core/trade.hpp"
#include "../include/core/transaction_cost.hpp"
#include "../include/data/data_loader.hpp"
#include "../include/data/market_data.hpp"
#include "../include/data/strategy_parameter.hpp"
#include "../include/execution/execution_engine.hpp"
#include "../include/execution/execution_model.hpp"
#include "../include/execution/full_position_sizer.hpp"
#include "../include/execution/order_manager.hpp"
#include "../include/execution/order_validator.hpp"
#include "../include/indicator/rsi.hpp"
#include "../include/performance/performance_analyzer.hpp"
#include "../include/strategy/bollinger_strategy.hpp"
#include "../include/strategy/moving_average_strategy.hpp"
#include "../include/strategy/rsi_strategy.hpp"
#include "../include/visualization/print_backtest_summaries.hpp"

int main() {
  std::vector<MAParams> ma_params{
      {5, 20},
      {10, 30},
      {20, 60},
  };

  std::vector<BollingerParams> bollinger_params{
      {10, 2.0},
      {20, 2.0},
      {20, 2.5},
  };

  std::vector<RSIParams> rsi_params{
      {9, 30.0, 70.0},
      {14, 30.0, 70.0},
      {14, 25.0, 75.0},
  };

  std::vector<BacktestSummary> summaries;
  DataLoader loader(',');
  PriceFrame test_data =
      loader.load_csv("data/day_1/cleaned_sh600231_daily_qfq_tx.csv");

  // MA
  for (const auto& para : ma_params) {
    MovingAverageStrategy sma(
        para.short_window, para.long_window, &PriceBar::close);
    std::size_t periods_per_year = 252;
    BacktestSummary summary = run_backtest(
        "sh600231", TimeFrame::DAY_1, test_data, periods_per_year, sma);
    print_backtest_summary(summary);
  }

  // Bollinger
  for (const auto& para : bollinger_params) {
    BollingerStrategy bollinger(
        para.window, para.num_std_dev, &PriceBar::close);
    std::size_t periods_per_year = 252;
    BacktestSummary summary = run_backtest(
        "sh600231", TimeFrame::DAY_1, test_data, periods_per_year, bollinger);
    print_backtest_summary(summary);
  }

  // RSI
  for (const auto& para : rsi_params) {
    RSIStrategy rsi(para.window,
                    para.oversold_threshold,
                    para.overbought_threshold,
                    &PriceBar::close);
    std::size_t periods_per_year = 252;
    BacktestSummary summary = run_backtest(
        "sh600231", TimeFrame::DAY_1, test_data, periods_per_year, rsi);
    print_backtest_summary(summary);
  }

  /*
  Portfolio portfolio;
  portfolio.cash = 100000;

  std::cout << "Account Cash: " << portfolio.cash << '\n'
            << "Market Value: " << portfolio.market_value << '\n'
            << "Equity: " << portfolio.equity << '\n'
            << "Shares: " << portfolio.shares << '\n';
  DataLoader loader(',');
  PriceFrame test_data =
      loader.load_csv("data/day_1/cleaned_sh600231_daily_qfq_tx.csv");

  MarketData market_data;
  market_data.add_data("sh600231", TimeFrame::DAY_1, std::move(test_data));

  const PriceFrame& history =
      market_data.get_data("sh600231", TimeFrame::DAY_1);

  std::cout << history.size() << '\n';
  /*
  PriceFrame test_data{
      {"2026-01-01", "sh001", 20, 20, 20, 20, 1000},
      {"2026-01-02", "sh001", 18, 18, 18, 18, 1000},
      {"2026-01-03", "sh001", 16, 16, 16, 16, 1000},
      {"2026-01-04", "sh001", 14, 14, 14, 14, 1000},
      {"2026-01-05", "sh001", 12, 12, 12, 12, 1000},
      {"2026-01-06", "sh001", 14, 14, 14, 14, 1000},
      {"2026-01-07", "sh001", 17, 17, 17, 17, 1000},
      {"2026-01-08", "sh001", 20, 20, 20, 20, 1000},
      {"2026-01-09", "sh001", 23, 23, 23, 23, 1000},
      {"2026-01-10", "sh001", 26, 26, 26, 26, 1000},
  };


  // MovingAverageStrategy sma(3, 5);
  // BollingerStrategy boll(20, 2.0);
  RSIStrategy rsi(14, 30.0, 70.0);
  FullPositionSizer sizer;
  OrderManager manager;
  BacktestConfig config;
  TransactionCostModel cost_model(config);
  ExecutionModel execution_model(cost_model);
  OrderValidator order_validator(execution_model);
  ExecutionEngine execution(execution_model);

  // Backtester backtester(
  //    sma, sizer, manager, order_validator, execution, portfolio);

  // Backtester backtester(
  //     boll, sizer, manager, order_validator, execution, portfolio);

  Backtester backtester(
      rsi, sizer, manager, order_validator, execution, portfolio);

  BacktestResult result = backtester.run("sh600231", history);

  /*
MovingAverageStrategy strategy;

MarketSnapShot previous = {"2026-08-09", "sh0001", 10.0, 9.0, 10.0};
MarketSnapShot current = {"2026-08-09", "sh0001", 10.0, 12.0, 11.0};
double market_price = current.close;

Signal signal = strategy.generate_signal(previous, current);

FullPositionSizer sizer;

OrderManager manager;
std::optional<Order> order =
    manager.generate_order(signal, portfolio, current, sizer);

if (order) {
  std::cout << "\nOriginal Order\n"
            << "Order Symbol: " << order->symbol << '\n'
            << "Order Timestamp: " << order->timestamp << '\n'
            << "Order Side: " << to_string(order->side) << '\n'
            << "Order Quantity: " << order->quantity << '\n';
  BacktestConfig config;
  TransactionCostModel cost_model(config);
  ExecutionModel execution_model(cost_model);
  OrderValidator order_validator(execution_model);
  std::optional<Order> adjusted_order =
      order_validator.validate_order(*order, portfolio, market_price);

  std::cout << "\nAdjusted Order\n"
            << "Order Symbol: " << adjusted_order->symbol << '\n'
            << "Order Timestamp: " << adjusted_order->timestamp << '\n'
            << "Order Side: " << to_string(adjusted_order->side) << '\n'
            << "Order Quantity: " << adjusted_order->quantity << '\n';

  ExecutionEngine execution(execution_model);

  Trade trade = execution.execute(*adjusted_order, current.close);
  std::cout << "\nTrade Symbol: " << trade.symbol << '\n'
            << "Trade Time: " << trade.timestamp << '\n'
            << "Trade Type: " << to_string(trade.side) << '\n'
            << "Execution Price: " << trade.execution_price << '\n'
            << "Execution Quantity: " << trade.quantity << '\n'
            << "Commission: " << trade.commission << '\n'
            << "Stamp Duty: " << trade.stamp_duty << '\n'
            << "Slippage Cost: " << trade.slippage_cost << '\n';

  portfolio.apply_trade(trade);
  portfolio.update_market_value(market_price);
  std::cout << "\nAccount Cash: " << portfolio.cash << '\n'
            << "Market Value: " << portfolio.market_value << '\n'
            << "Equity: " << portfolio.equity << '\n'
            << "Shares: " << portfolio.shares << '\n';
} else {
  std::cout << "No orders and trades generated." << '\n';
}
return 0;

  std::cout << "Total Return: " << PerformanceAnalyzer::total_return(result)
            << '\n';

  std::cout << "Annualized Return: "
            << PerformanceAnalyzer::annualized_return(result, 252) << '\n';

  std::cout << "Annualized Volatility: "
            << PerformanceAnalyzer::annualized_volatility(result, 252) << '\n';

  std::cout << "Sharpe Ratio: "
            << PerformanceAnalyzer::sharpe_ratio(result, 0.0, 252) << '\n';

  std::cout << "Max Drawdown: " << PerformanceAnalyzer::max_drawdown(result)
            << '\n';
  std::cout << "Sortino Ratio: "
            << PerformanceAnalyzer::sortino_ratio(result, 0.0, 252) << '\n';
  std::cout << "Calmar Ratio: "
            << PerformanceAnalyzer::calmar_ratio(result, 252) << '\n';

  ClosedTradeHistory closed_trades =
      PerformanceAnalyzer::extract_closed_trades(result);

  std::cout << "Closed Trades: " << closed_trades.size() << '\n';

  std::cout << "Win Rate: " << PerformanceAnalyzer::win_rate(closed_trades)
            << '\n';

  std::cout << "Average Win: "
            << PerformanceAnalyzer::average_win(closed_trades) << '\n';

  std::cout << "Average Loss: "
            << PerformanceAnalyzer::average_loss(closed_trades) << '\n';

  std::cout << "Profit-Loss Ratio: "
            << PerformanceAnalyzer::profit_loss_ratio(closed_trades) << '\n';

  std::cout << "Max Win: " << PerformanceAnalyzer::max_win(closed_trades)
            << '\n';

  std::cout << "Max Loss: " << PerformanceAnalyzer::max_loss(closed_trades)
            << '\n';

  std::cout << history.size() << '\n';
  std::cout << result.equity_history.size() << '\n';

  std::cout << "Trade Details: " << '\n';
  for (const auto& closed_trade : closed_trades) {
    std::cout << "\nSymbol: " << closed_trade.symbol << '\n'
              << "Entry Timestamp: " << closed_trade.entry_timestamp << '\n'
              << "Exit Timestamp: " << closed_trade.exit_timestamp << '\n'
              << "Quantity: " << closed_trade.quantity << '\n'
              << "Entry Price: " << closed_trade.entry_price << '\n'
              << "Exit Price: " << closed_trade.exit_price << '\n'
              << "Profit & Loss: " << closed_trade.pnl << '\n'
              << "Return Rate: " << closed_trade.return_rate << '\n';
  }
  /*
  TimeSeries rising_prices{
      {"t0", 1.0},
      {"t1", 2.0},
      {"t2", 3.0},
      {"t3", 4.0},
      {"t4", 5.0},
      {"t5", 6.0},
  };

  TimeSeries falling_prices{
      {"t0", 6.0},
      {"t1", 5.0},
      {"t2", 4.0},
      {"t3", 3.0},
      {"t4", 2.0},
      {"t5", 1.0},
  };

  TimeSeries flat_prices{
      {"t0", 3.0},
      {"t1", 3.0},
      {"t2", 3.0},
      {"t3", 3.0},
      {"t4", 3.0},
      {"t5", 3.0},
  };

  std::cout << "Rising RSI: " << calculate_rsi(rising_prices, 5, 5) << '\n';

  std::cout << "Falling RSI: " << calculate_rsi(falling_prices, 5, 5) << '\n';

  std::cout << "Flat RSI: " << calculate_rsi(flat_prices, 5, 5) << '\n';

  TimeSeries mixed_prices{
      {"t0", 10.0},
      {"t1", 12.0},  // +2
      {"t2", 11.0},  // -1
      {"t3", 14.0},  // +3
      {"t4", 12.0},  // -2
      {"t5", 13.0},  // +1
  };
  std::cout << "Mixed RSI: " << calculate_rsi(mixed_prices, 5, 5) << '\n';
  */
}
