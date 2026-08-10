#include "../../include/execution/execution_model.hpp"

#include <stdexcept>

ExecutionModel::ExecutionModel(const TransactionCostModel& cost_model)
    : cost_model_(cost_model) {}

ExecutionQuote ExecutionModel::generate_quote(const Order& order,
                                              double market_price) const {
  if (order.side == OrderSide::HOLD) {
    throw std::runtime_error("HOLD is not a valid order side.");
  }
  if (order.quantity <= 0) {
    throw std::runtime_error("Order quantity must be positive.");
  }

  double execution_price = (order.side == OrderSide::BUY)
                               ? market_price * (1 + cost_model_.slippage_rate)
                               : market_price * (1 - cost_model_.slippage_rate);

  double trade_value = execution_price * order.quantity;
  double commission = cost_model_.calculate_commission(trade_value);
  double stamp_duty = cost_model_.calculate_stamp_duty(trade_value, order.side);
  double slippage_cost = cost_model_.calculate_slippage(
      market_price, execution_price, order.quantity);

  double total_fee = commission + stamp_duty;

  return ExecutionQuote{
      .execution_price = execution_price,
      .quantity = order.quantity,
      .trade_value = trade_value,
      .commission = commission,
      .stamp_duty = stamp_duty,
      .slippage_cost = slippage_cost,
      .total_fee = total_fee,
  };
}
