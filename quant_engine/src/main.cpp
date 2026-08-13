#include <chrono>
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

  for (const auto& symbol : symbols) {
    for (const auto timeframe : timeframes) {
      const std::size_t periods_per_year = get_periods_per_year(timeframe);

      const PriceFrame& data_frame = market_data.get_data(symbol, timeframe);

      for (const auto strategy_type : strategy_type_list) {
        switch (strategy_type) {
          case StrategyType::MOVINGAVERGAE: {
            std::vector<BacktestSummary> summaries_ma;

            for (const auto& para : ma_params) {
              MovingAverageStrategy sma(para.short_window, para.long_window, &PriceBar::close);

              std::cerr << "[START] " << symbol << " " << to_string(timeframe) << " " << sma.name()
                        << " " << sma.parameters() << '\n';

              auto start = std::chrono::steady_clock::now();

              BacktestSummary summary =
                  run_backtest(symbol, timeframe, data_frame, periods_per_year, sma);
              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " " << sma.name()
                        << " " << sma.parameters() << ": " << duration.count() << " ms\n";

              std::cerr << "[DONE] " << symbol << " " << to_string(timeframe) << " " << sma.name()
                        << " " << sma.parameters() << '\n';

              summaries_ma.push_back(summary);

              print_backtest_summary(summary);
            }

            ParameterSensitivity sensitity = analyze_parameter_sensitivity(summaries_ma);
            break;
          }

          case StrategyType::BOLLINGER: {
            std::vector<BacktestSummary> summaries_bollinger;
            for (const auto& para : bollinger_params) {
              BollingerStrategy bollinger(para.window, para.num_std_dev, &PriceBar::close);

              std::cerr << "[START] " << symbol << " " << to_string(timeframe) << " "
                        << bollinger.parameters() << '\n';

              auto start = std::chrono::steady_clock::now();

              BacktestSummary summary =
                  run_backtest(symbol, timeframe, data_frame, periods_per_year, bollinger);
              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " "
                        << bollinger.name() << " " << bollinger.parameters() << ": "
                        << duration.count() << " ms\n";

              std::cerr << "[DONE] " << symbol << " " << to_string(timeframe) << " "
                        << bollinger.parameters() << '\n';

              summaries_bollinger.push_back(summary);

              print_backtest_summary(summary);
            }

            ParameterSensitivity sensitity = analyze_parameter_sensitivity(summaries_bollinger);
            break;
          }

          case StrategyType::RSI: {
            std::vector<BacktestSummary> summaries_rsi;
            for (const auto& para : rsi_params) {
              RSIStrategy rsi(
                  para.window,
                  para.oversold_threshold,
                  para.overbought_threshold,
                  &PriceBar::close
              );

              std::cerr << "[START] " << symbol << " " << to_string(timeframe) << " "
                        << rsi.parameters() << '\n';

              auto start = std::chrono::steady_clock::now();

              BacktestSummary summary =
                  run_backtest(symbol, timeframe, data_frame, periods_per_year, rsi);

              auto end = std::chrono::steady_clock::now();

              auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

              std::cerr << "[TIME] " << symbol << " " << to_string(timeframe) << " " << rsi.name()
                        << " " << rsi.parameters() << ": " << duration.count() << " ms\n";

              std::cerr << "[DONE] " << symbol << " " << to_string(timeframe) << " "
                        << rsi.parameters() << '\n';

              summaries_rsi.push_back(summary);

              print_backtest_summary(summary);
            }

            ParameterSensitivity sensitity = analyze_parameter_sensitivity(summaries_rsi);
            break;
          }
        }
      }
    }
  }
}
