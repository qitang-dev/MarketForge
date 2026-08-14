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

ParameterSensitivity analyze_parameter_sensitivity(const std::vector<BacktestRun>& runs) {
  if (runs.size() < 2) {
    throw std::invalid_argument("At least 2 summaries are needed for the target strategy.");
  }
  std::vector<BacktestRun> runs_copy = runs;

  std::sort(
      runs_copy.begin(),
      runs_copy.end(),

      [](const BacktestRun& a, const BacktestRun& b) {
        return a.summary.total_return > b.summary.total_return;
      }
  );

  auto best = runs_copy.begin();
  auto second_best = std::next(best);

  double return_gap = best->summary.total_return - second_best->summary.total_return;

  return ParameterSensitivity{
      .symbol = best->summary.symbol,
      .timeframe = best->summary.timeframe,
      .strategy_name = best->summary.strategy_name,
      .best = best->summary,
      .second_best = second_best->summary,
      .best_history = best->result,
      .return_gap = return_gap,
  };
}
