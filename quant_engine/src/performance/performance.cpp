#include <cmath>

#include "../../include/data/constant.hpp"
#include "../../include/data/data_utils.hpp"
#include "../../include/performance/performance_analyzer.hpp"

TimeSeries extract_equity_curve(const BacktestResult& result) {
  TimeSeries equity_curve;
  equity_curve.reserve(result.equity_history.size());
  for (const auto& point : result.equity_history) {
    equity_curve.push_back(TimeSeriesPoint{
        .timestamp = point.timestamp,
        .value = point.equity,
    });
  }
  return equity_curve;
}

TimeSeries simple_return(const TimeSeries& values) {
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

TimeSeries drawdown(const TimeSeries& equity_curve) {
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

    const double current_drawdown =
        (running_peak == 0.0) ? NaN : point.value / running_peak - 1.0;

    drawdowns.push_back(TimeSeriesPoint{point.timestamp, current_drawdown});
  }
}

double total_return(const BacktestResult& result) {
  if (result.equity_history.empty()) return NaN;

  const double initial_equity = result.equity_history.front().equity;
  const double final_equity = result.equity_history.back().equity;

  if (initial_equity == 0.0) return NaN;
  return final_equity / initial_equity - 1.0;
}

double annualized_return(const BacktestResult& result,
                         std::size_t periods_per_year = 252) {
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

  const double exponent = static_cast<double>(periods_per_year) /
                          static_cast<double>(valid_periods);
  return std::pow(total_growth, exponent) - 1.0;
}

double annualized_volatility(const BacktestResult& result,
                             std::size_t periods_per_year = 252) {
  const TimeSeries returns = simple_return(extract_equity_curve(result));
  if (periods_per_year == 0) return NaN;
  const double period_volatility = stdev(returns);
  return period_volatility * std::sqrt(static_cast<double>(periods_per_year));
}

double sharpe_ratio(const BacktestResult& result,
                    double risk_free_rate = 0.0,
                    std::size_t periods_per_year = 252) {
  if (periods_per_year == 0 || risk_free_rate <= -1.0) {
    return NaN;
  }
  const TimeSeries returns = simple_return(extract_equity_curve(result));
  if (returns.size() < 2) return NaN;

  const double double_year = static_cast<double>(periods_per_year);

  double period_risk_free_rate =
      std::pow((1.0 + risk_free_rate), (1.0 / double_year)) - 1.0;

  TimeSeries excess_returns;
  excess_returns.reserve(returns.size());

  for (const auto& point : returns) {
    if (std::isnan(point.value)) {
      excess_returns.push_back(TimeSeriesPoint{point.timestamp, NaN});
    } else {
      excess_returns.push_back(TimeSeriesPoint{
          point.timestamp, (point.value - period_risk_free_rate)});
    }
  }
  const double mean_excess_return = mean(excess_returns);
  const double excess_volatility = stdev(excess_returns);

  if (std::isnan(mean_excess_return) || std::isnan(excess_volatility) ||
      excess_volatility == 0.0) {
    return NaN;
  }

  return mean_excess_return / excess_volatility * std::sqrt(double_year);
}

double max_drawdown(const BacktestResult& result) {
  const TimeSeries equity_curve = extract_equity_curve(result);
  return min(drawdown(equity_curve));
}