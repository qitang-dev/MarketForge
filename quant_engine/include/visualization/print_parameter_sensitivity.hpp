#pragma once
#include <iomanip>
#include <iostream>

#include "../data/backtest_result.hpp"
#include "../data/market_data.hpp"

void print_parameter_sensitivity(std::ostream& os, const ParameterSensitivity& sensitivity) {
  os << "======= Parameter Sensitivity =======\n";

  os << std::left << std::setw(24) << "Symbol:" << sensitivity.best.symbol << '\n';

  os << std::left << std::setw(24) << "Timeframe:" << to_string(sensitivity.best.timeframe) << '\n';

  os << std::left << std::setw(24) << "Strategy:" << sensitivity.best.strategy_name << '\n';

  os << "-------------------------------------\n";

  os << std::left << std::setw(24) << "Best Parameters:" << sensitivity.best.parameters << '\n';

  os << std::left << std::setw(24) << "Best Return:" << std::fixed << std::setprecision(2)
     << sensitivity.best.total_return * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Second Parameters:" << sensitivity.second_best.parameters
     << '\n';

  os << std::left << std::setw(24)
     << "Second Return:" << sensitivity.second_best.total_return * 100.0 << "%\n";

  os << std::left << std::setw(24) << "Return Gap:" << sensitivity.return_gap * 100.0 << "%\n";

  os << "=====================================\n";
}