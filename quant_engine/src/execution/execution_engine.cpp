#include "../../include/execution/execution_engine.hpp"

#include <stdexcept>

ExecutionEngine::ExecutionEngine(const ExecutionModel& execution_model)
    : execution_model_(execution_model) {}

Trade ExecutionEngine::execute(const Order& valid_order, double market_price) {
  if (valid_order.side == OrderSide::HOLD) {
    throw std::runtime_error("HOLD order cannot be executed.");
  }
  const ExecutionQuote kExecutionQuote =
      execution_model_.generate_quote(valid_order, market_price);

  return Trade{
      .symbol = valid_order.symbol,
      .timestamp = valid_order.timestamp,
      .side = valid_order.side,
      .quantity = valid_order.quantity,
      .execution_price = kExecutionQuote.execution_price,
      .commission = kExecutionQuote.commission,
      .stamp_duty = kExecutionQuote.stamp_duty,
      .slippage_cost = kExecutionQuote.slippage_cost,
  };
}
