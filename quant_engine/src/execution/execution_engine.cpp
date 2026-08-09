#include "../../include/execution/execution_engine.hpp"

#include <stdexcept>

ExecutionEngine::ExecutionEngine(const TransactionCostModel& cost_model)
    : cost_model_(cost_model) {}

Trade ExecutionEngine::execute(const Order& order, double market_price) {
  if (order.side == OrderSide::HOLD) {
    throw std::runtime_error("HOLD order cannot be executed.");
  }
  double slippage_rate = cost_model_.slippage_rate;

  double execution_price = (order.side == OrderSide::BUY)
                               ? market_price * (1 + slippage_rate)
                               : market_price * (1 - slippage_rate);

  double trade_value = execution_price * order.quantity;

  double commission = cost_model_.calculate_commission(trade_value);
  double stamp_duty = cost_model_.calculate_stamp_duty(trade_value, order.side);
  double slippage_cost = cost_model_.calculate_slippage(
      market_price, execution_price, order.quantity);

  return Trade{order.timestamp, order.symbol, order.side, order.quantity,
               execution_price, commission,   stamp_duty, slippage_cost};
}