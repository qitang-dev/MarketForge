#include "../../include/performance/performance_analyzer.hpp"

#include <algorithm>
#include <cmath>

#include "../../include/data/constant.hpp"
#include "../../include/data/data_utils.hpp"

TimeSeries PerformanceAnalyzer::extract_equity_curve(const BacktestResult& result) {
  TimeSeries equity_curve;
  equity_curve.reserve(result.equity_history.size());
  for (const auto& point : result.equity_history) {
    equity_curve.push_back(
        TimeSeriesPoint{
            .timestamp = point.timestamp,
            .value = point.equity,
        }
    );
  }
  return equity_curve;
}

ClosedTradeHistory PerformanceAnalyzer::extract_closed_trades(const BacktestResult& result) {
  ClosedTradeHistory closed_trades;
  const Trade* entry_trade = nullptr;
  for (const auto& trade : result.trade_history) {
    if (trade.side == OrderSide::BUY) {
      if (entry_trade == nullptr) {
        entry_trade = &trade;
      }
    } else if (trade.side == OrderSide::SELL) {
      if (entry_trade == nullptr) {
        continue;
      }
      const double entry_cost = entry_trade->execution_price * entry_trade->quantity +
                                entry_trade->commission + entry_trade->stamp_duty;

      const double exit_proceeds =
          trade.execution_price * trade.quantity - trade.commission - trade.stamp_duty;

      const double pnl = exit_proceeds - entry_cost;

      const double return_rate = (entry_cost == 0.0) ? NaN : pnl / entry_cost;

      closed_trades.push_back(
          ClosedTrade{
              .symbol = entry_trade->symbol,
              .entry_timestamp = entry_trade->timestamp,
              .exit_timestamp = trade.timestamp,
              .quantity = trade.quantity,
              .entry_price = entry_trade->execution_price,
              .exit_price = trade.execution_price,
              .pnl = pnl,
              .return_rate = return_rate,
          }
      );

      entry_trade = nullptr;
    }
  }
  return closed_trades;
}

TimeSeries PerformanceAnalyzer::simple_return(const TimeSeries& values) {
  TimeSeries returns;
  returns.reserve(values.size());

  if (values.empty()) return returns;

  returns.push_back(TimeSeriesPoint{values[0].timestamp, NaN});

  for (std::size_t i = 1; i < values.size(); ++i) {
    if (std::isnan(values[i].value) || std::isnan(values[i - 1].value) ||
        values[i - 1].value == 0.0) {
      returns.push_back(TimeSeriesPoint{values[i].timestamp, NaN});
      continue;
    }

    double period_return = values[i].value / values[i - 1].value - 1.0;
    returns.push_back(TimeSeriesPoint{values[i].timestamp, period_return});
  }

  return returns;
}

TimeSeries PerformanceAnalyzer::drawdown(const TimeSeries& equity_curve) {
  TimeSeries drawdowns;
  drawdowns.reserve(equity_curve.size());

  if (equity_curve.empty()) return drawdowns;

  double running_peak = NaN;

  for (const auto& point : equity_curve) {
    if (std::isnan(point.value)) {
      drawdowns.push_back(TimeSeriesPoint{point.timestamp, NaN});
      continue;
    }

    if (std::isnan(running_peak) || point.value > running_peak) {
      running_peak = point.value;
    }

    const double current_drawdown = (running_peak == 0.0) ? NaN : point.value / running_peak - 1.0;

    drawdowns.push_back(TimeSeriesPoint{point.timestamp, current_drawdown});
  }
  return drawdowns;
}

double PerformanceAnalyzer::total_return(const BacktestResult& result) {
  if (result.equity_history.empty()) return NaN;

  const double initial_equity = result.equity_history.front().equity;
  const double final_equity = result.equity_history.back().equity;

  if (initial_equity == 0.0) return NaN;

  return final_equity / initial_equity - 1.0;
}

double PerformanceAnalyzer::annualized_return(
    const BacktestResult& result, std::size_t periods_per_year
) {
  const TimeSeries returns = simple_return(extract_equity_curve(result));

  if (returns.size() < 2 || periods_per_year == 0) return NaN;

  double total_growth = 1.0;
  std::size_t valid_periods = 0;

  for (const auto& point : returns) {
    if (std::isnan(point.value)) continue;

    total_growth *= (1.0 + point.value);
    ++valid_periods;
  }

  if (valid_periods == 0 || total_growth <= 0.0) return NaN;

  const double exponent =
      static_cast<double>(periods_per_year) / static_cast<double>(valid_periods);

  return std::pow(total_growth, exponent) - 1.0;
}

double PerformanceAnalyzer::annualized_volatility(
    const BacktestResult& result, std::size_t periods_per_year
) {
  const TimeSeries returns = simple_return(extract_equity_curve(result));

  if (periods_per_year == 0) return NaN;

  const double period_volatility = stdev(returns);

  return period_volatility * std::sqrt(static_cast<double>(periods_per_year));
}

double PerformanceAnalyzer::sharpe_ratio(
    const BacktestResult& result, double risk_free_rate, std::size_t periods_per_year
) {
  if (periods_per_year == 0 || risk_free_rate <= -1.0) {
    return NaN;
  }

  const TimeSeries returns = simple_return(extract_equity_curve(result));
  if (returns.size() < 2) return NaN;

  const double double_year = static_cast<double>(periods_per_year);

  double period_risk_free_rate = std::pow((1.0 + risk_free_rate), (1.0 / double_year)) - 1.0;

  TimeSeries excess_returns;
  excess_returns.reserve(returns.size());

  for (const auto& point : returns) {
    if (std::isnan(point.value)) {
      excess_returns.push_back(TimeSeriesPoint{point.timestamp, NaN});
    } else {
      excess_returns.push_back(
          TimeSeriesPoint{point.timestamp, (point.value - period_risk_free_rate)}
      );
    }
  }
  const double mean_excess_return = mean(excess_returns);
  const double excess_volatility = stdev(excess_returns);

  if (std::isnan(mean_excess_return) || std::isnan(excess_volatility) || excess_volatility == 0.0) {
    return NaN;
  }

  return mean_excess_return / excess_volatility * std::sqrt(double_year);
}

double PerformanceAnalyzer::max_drawdown(const BacktestResult& result) {
  const TimeSeries equity_curve = extract_equity_curve(result);
  return min(drawdown(equity_curve));
}

double PerformanceAnalyzer::average_win(const ClosedTradeHistory& closed_trades) {
  double total_win = 0.0;
  std::size_t win_count = 0;

  for (const auto& closed_trade : closed_trades) {
    if (closed_trade.pnl > 0.0) {
      total_win += closed_trade.pnl;
      ++win_count;
    }
  }

  if (win_count == 0) {
    return NaN;
  }
  return total_win / static_cast<double>(win_count);
}

double PerformanceAnalyzer::average_loss(const ClosedTradeHistory& closed_trades) {
  double total_loss = 0.0;
  std::size_t loss_count = 0;

  for (const auto& closed_trade : closed_trades) {
    if (closed_trade.pnl < 0.0) {
      total_loss += closed_trade.pnl;
      ++loss_count;
    }
  }

  if (loss_count == 0) {
    return NaN;
  }

  return total_loss / static_cast<double>(loss_count);
}

double PerformanceAnalyzer::profit_loss_ratio(const ClosedTradeHistory& closed_trades) {
  const double avg_win = average_win(closed_trades);
  const double avg_loss = average_loss(closed_trades);

  if (std::isnan(avg_win) || std::isnan(avg_loss) || avg_loss == 0) {
    return NaN;
  }

  return avg_win / std::abs(avg_loss);
}

double PerformanceAnalyzer::sortino_ratio(
    const BacktestResult& result, double risk_free_rate, std::size_t periods_per_year
) {
  if (periods_per_year == 0 || risk_free_rate <= -1.0) {
    return NaN;
  }

  const TimeSeries returns = simple_return(extract_equity_curve(result));

  const double periods = static_cast<double>(periods_per_year);

  const double period_risk_free_rate = std::pow(1.0 + risk_free_rate, 1.0 / periods) - 1.0;

  double excess_sum = 0.0;

  double downside_sq_sum = 0.0;

  std::size_t valid_count = 0;

  for (const auto& point : returns) {
    if (std::isnan(point.value)) {
      continue;
    }

    const double excess_return = point.value - period_risk_free_rate;

    excess_sum += excess_return;

    if (excess_return < 0.0) {
      downside_sq_sum += excess_return * excess_return;
    }

    ++valid_count;
  }

  if (valid_count == 0) {
    return NaN;
  }

  const double mean_excess_return = excess_sum / static_cast<double>(valid_count);

  const double downside_deviation = std::sqrt(downside_sq_sum / static_cast<double>(valid_count));

  if (downside_deviation == 0.0) {
    return NaN;
  }

  return mean_excess_return / downside_deviation * std::sqrt(periods);
}

double PerformanceAnalyzer::calmar_ratio(
    const BacktestResult& result, std::size_t periods_per_year
) {
  const double annual_return = annualized_return(result, periods_per_year);

  const double mdd = max_drawdown(result);

  if (std::isnan(annual_return) || std::isnan(mdd) || mdd == 0.0) {
    return NaN;
  }

  return annual_return / std::abs(mdd);
}

double PerformanceAnalyzer::win_rate(const ClosedTradeHistory& closed_trades) {
  if (closed_trades.empty()) return NaN;

  std::size_t win_count = 0;
  for (const auto& closed_trade : closed_trades) {
    if (closed_trade.pnl > 0) {
      ++win_count;
    }
  }
  return static_cast<double>(win_count) / static_cast<double>(closed_trades.size());
}

double PerformanceAnalyzer::max_win(const ClosedTradeHistory& closed_trades) {
  auto it = std::max_element(
      closed_trades.begin(),
      closed_trades.end(),
      [](const ClosedTrade& a, const ClosedTrade& b) { return a.pnl < b.pnl; }
  );
  if (it == closed_trades.end() || it->pnl <= 0.0) {
    return NaN;
  }
  return it->pnl;
}

double PerformanceAnalyzer::max_loss(const ClosedTradeHistory& closed_trades) {
  auto it = std::min_element(
      closed_trades.begin(),
      closed_trades.end(),
      [](const ClosedTrade& a, const ClosedTrade& b) { return a.pnl < b.pnl; }
  );

  if (it == closed_trades.end() || it->pnl >= 0.0) {
    return NaN;
  }
  return it->pnl;
}