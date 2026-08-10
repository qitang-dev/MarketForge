#include "../../include/execution/order_validator.hpp"

#include "../../include/core/backtest_config.hpp"

OrderValidator::OrderValidator(const ExecutionModel& execution_model)
    : execution_model_(execution_model) {}

std::optional<Order> OrderValidator::validate_order(const Order& order,
                                                    const Portfolio& portfolio,
                                                    double market_price) const {
  Order adjusted_order = order;
  adjusted_order.quantity = (adjusted_order.quantity / LOT_SIZE_A) * LOT_SIZE_A;

  if (order.side == OrderSide::BUY) {
    while (adjusted_order.quantity > 0) {
      ExecutionQuote buy_quote =
          execution_model_.generate_quote(adjusted_order, market_price);
      if (portfolio.cash >= (buy_quote.trade_value + buy_quote.total_fee)) {
        return adjusted_order;
      }
      adjusted_order.quantity -= LOT_SIZE_A;
    }
    return std::nullopt;

  } else if (order.side == OrderSide::BUY) {
    if (portfolio.shares <= 0) {
      return std::nullopt;
    }
    adjusted_order.quantity = std::min(portfolio.shares, order.quantity);
    ExecutionQuote sell_quote =
        execution_model_.generate_quote(adjusted_order, market_price);

    if (sell_quote.trade_value <= sell_quote.total_fee) {
      return std::nullopt;
    }
    return adjusted_order;
  } else {
    return std::nullopt;
  }
}
