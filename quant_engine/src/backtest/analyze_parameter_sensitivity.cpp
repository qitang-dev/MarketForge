#include "../../include/backtest/analyze_parameter_sensitivity.hpp"

#include <algorithm>
#include <iterator>
#include <stdexcept>

std::pair<BacktestSummary, BacktestSummary> analyze_parameter_sensitivity(
    const std::string& symbol_name,
    TimeFrame timeframe,
    const std::string& strategy_name,
    const std::vector<BacktestSummary>& summaries
) {
  std::vector<BacktestSummary> target_summaries;

  for (auto it = summaries.begin(); it != summaries.end(); ++it) {
    if (it->symbol == symbol_name && it->timeframe == timeframe &&
        it->strategy_name == strategy_name) {
      target_summaries.push_back(*it);
    }
  }

  if (target_summaries.size() < 2) {
    throw std::invalid_argument(
        "At least 2 summaries are needed for the target strategy analysis."
    );
  }

  std::sort(
      target_summaries.begin(),
      target_summaries.end(),
      [](const BacktestSummary& a, const BacktestSummary& b) {
        return a.total_return > b.total_return;
      }
  );

  auto best = target_summaries.begin();
  auto second_best = std::next(best);

  return {*best, *second_best};
}

ParameterSensitivity analyze_parameter_sensitivity(const std::vector<BacktestSummary>& summaries) {
  if (summaries.size() < 2) {
    throw std::invalid_argument("At least 2 summaries are needed for the target strategy.");
  }
  std::vector<BacktestSummary> summaries_copy = summaries;
  std::sort(
      summaries_copy.begin(),
      summaries_copy.end(),
      [](const BacktestSummary& a, const BacktestSummary& b) {
        return a.total_return > b.total_return;
      }
  );

  auto best = summaries_copy.begin();
  auto second_best = std::next(best);

  double return_gap = best->total_return - second_best->total_return;

  return ParameterSensitivity{
      .symbol = best->symbol,
      .timeframe = best->timeframe,
      .strategy_name = best->strategy_name,
      .best = *best,
      .second_best = *second_best,
      .return_gap = return_gap,
  };
}
