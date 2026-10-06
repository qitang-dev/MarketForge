#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

#include "../include/backtest/analyze_parameter_sensitivity.hpp"
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
#include "../include/data/strategy_type.hpp"
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
#include "../include/visualization/print_parameter_sensitivity.hpp"
#include "../include/visualization/write_strategy_report.hpp"

int main() {
  const std::vector<std::string> symbols{
      "sz002067",
      "sz002600",
      "sz002230",
      "sh600763",
      "sh603259",
      "sh603799",
      "sh601012",
      "sh600438",
      "sz002361",
      "sh601500",
      "sh600231",
      "sz300274",
      "sh601636",
      "sz002129",
      "sz000100",
      "sz300433",

  };

  const std::vector<TimeFrame> timeframes{
      TimeFrame::DAY_1,
      TimeFrame::MIN_5,
  };

  const std::vector<StrategyType> strategy_type_list{
      StrategyType::MOVINGAVERGAE,
      StrategyType::BOLLINGER,
      StrategyType::RSI,
  };

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

  const double kInitialCash = 100000;

  MarketData market_data;
  DataLoader loader(',');

  for (const auto& symbol : symbols) {
    for (const auto timeframe : timeframes) {
      const std::string time_scale = get_str_time_scale(timeframe);

      const std::string file_path =
          "data/" + time_scale + "/" + symbol + "_" + time_scale + "_qfq.csv";

      PriceFrame data_frame = loader.load_csv(file_path);

      market_data.add_data(symbol, timeframe, std::move(data_frame));
    }
  }

  const std::filesystem::path summary_dir = "report/backtest_summary";
  const std::filesystem::path sensitivity_dir = "report/strategy_parameter_sensitivity";
  const std::filesystem::path best_equity_history_dir = "report/best_equity_history";
  const std::filesystem::path best_trade_history_dir = "report/best_trade_history";

  std::filesystem::create_directories(summary_dir);
  std::filesystem::create_directories(sensitivity_dir);
  std::filesystem::create_directories(best_equity_history_dir);
  std::filesystem::create_directories(best_trade_history_dir);

  for (const auto& symbol : symbols) {
    std::filesystem::path symbol_summary_dir = summary_dir / symbol;
    std::filesystem::path symbol_sensitivity_dir = sensitivity_dir / symbol;
    std::filesystem::path symbol_best_equity_history_dir = best_equity_history_dir / symbol;
    std::filesystem::path symbol_best_trade_history_dir = best_trade_history_dir / symbol;

    for (const auto timeframe : timeframes) {
      const std::size_t periods_per_year = get_periods_per_year(timeframe);

      const PriceFrame& data_frame = market_data.get_data(symbol, timeframe);

      for (const auto strategy_type : strategy_type_list) {
        switch (strategy_type) {
          case StrategyType::MOVINGAVERGAE: {
            std::vector<BacktestRun> ma_runs;

            for (const auto& para : ma_params) {
              MovingAverageStrategy sma(para.short_window, para.long_window, &PriceBar::close);

              auto start = std::chrono::steady_clock::now();

              BacktestRun run =
                  run_backtest(symbol, timeframe, data_frame, periods_per_year, kInitialCash, sma);
              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " " << sma.name()
                        << " " << sma.parameters() << ": " << duration.count() << " ms\n";

              ma_runs.push_back(run);

              print_backtest_summary(std::cout, run.summary);
            }

            ParameterSensitivity sensitivity = analyze_parameter_sensitivity(ma_runs);

            const auto buy_hold = calculate_buy_hold_curve(data_frame, kInitialCash);

            const auto drawdowns =
                calculate_drawdown_curve(sensitivity.best_history.equity_history);

            const std::string summary_file_name =
                symbol + "_" + to_string(timeframe) + "_MovingAverage.txt";

            const std::string equity_history_file_name =
                "best_MovingAverage_equity_" + to_string(timeframe) + ".csv";

            const std::string trade_history_file_name =
                "best_MovingAverage_trade_" + to_string(timeframe) + ".csv";

            write_strategy_report(
                symbol_summary_dir,
                symbol_sensitivity_dir,
                symbol_best_equity_history_dir,
                symbol_best_trade_history_dir,
                summary_file_name,
                equity_history_file_name,
                trade_history_file_name,
                ma_runs,
                sensitivity,
                buy_hold,
                drawdowns
            );

            break;
          }

          case StrategyType::BOLLINGER: {
            std::vector<BacktestRun> bollinger_runs;

            for (const auto& para : bollinger_params) {
              BollingerStrategy bollinger(para.window, para.num_std_dev, &PriceBar::close);

              auto start = std::chrono::steady_clock::now();

              BacktestRun run = run_backtest(
                  symbol,
                  timeframe,
                  data_frame,
                  periods_per_year,
                  kInitialCash,
                  bollinger
              );
              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " "
                        << bollinger.name() << " " << bollinger.parameters() << ": "
                        << duration.count() << " ms\n";

              bollinger_runs.push_back(run);

              print_backtest_summary(std::cout, run.summary);
            }

            const ParameterSensitivity sensitivity = analyze_parameter_sensitivity(bollinger_runs);

            const auto buy_hold = calculate_buy_hold_curve(data_frame, kInitialCash);

            const auto drawdowns =
                calculate_drawdown_curve(sensitivity.best_history.equity_history);

            const std::string summary_file_name =
                symbol + "_" + to_string(timeframe) + "_Bollinger.txt";

            const std::string equity_history_file_name =
                "best_Bollinger_equity_" + to_string(timeframe) + ".csv";

            const std::string trade_history_file_name =
                "best_Bollinger_trade_" + to_string(timeframe) + ".csv";

            write_strategy_report(
                symbol_summary_dir,
                symbol_sensitivity_dir,
                symbol_best_equity_history_dir,
                symbol_best_trade_history_dir,
                summary_file_name,
                equity_history_file_name,
                trade_history_file_name,
                bollinger_runs,
                sensitivity,
                buy_hold,
                drawdowns
            );

            break;
          }

          case StrategyType::RSI: {
            std::vector<BacktestRun> rsi_runs;
            for (const auto& para : rsi_params) {
              RSIStrategy rsi(
                  para.window,
                  para.oversold_threshold,
                  para.overbought_threshold,
                  &PriceBar::close
              );

              auto start = std::chrono::steady_clock::now();

              BacktestRun run =
                  run_backtest(symbol, timeframe, data_frame, periods_per_year, kInitialCash, rsi);

              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " " << rsi.name()
                        << " " << rsi.parameters() << ": " << duration.count() << " ms\n";

              rsi_runs.push_back(run);

              print_backtest_summary(std::cout, run.summary);
            }

            ParameterSensitivity sensitivity = analyze_parameter_sensitivity(rsi_runs);

            const auto buy_hold = calculate_buy_hold_curve(data_frame, kInitialCash);

            const auto drawdowns =
                calculate_drawdown_curve(sensitivity.best_history.equity_history);

            const std::string summary_file_name = symbol + "_" + to_string(timeframe) + "_RSI.txt";

            const std::string equity_history_file_name =
                "best_RSI_equity_" + to_string(timeframe) + ".csv";

            const std::string trade_history_file_name =
                "best_RSI_trade_" + to_string(timeframe) + ".csv";

            write_strategy_report(
                symbol_summary_dir,
                symbol_sensitivity_dir,
                symbol_best_equity_history_dir,
                symbol_best_trade_history_dir,
                summary_file_name,
                equity_history_file_name,
                trade_history_file_name,
                rsi_runs,
                sensitivity,
                buy_hold,
                drawdowns
            );

            break;
          }
        }
      }
    }
  }
  return 0;
}
