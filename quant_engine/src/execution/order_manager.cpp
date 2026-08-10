#include "../../include/execution/order_manager.hpp"

#include <optional>
#include <stdexcept>

std::optional<Order> OrderManager::generate_order(
    const Signal& signal, const Portfolio& portfolio,
    const MarketSnapShot& snapshot, const PositionSizer& sizer) {
  if (signal.type == SignalType::HOLD) return std::nullopt;

  Order order;
  order.timestamp = snapshot.timestamp;
  order.symbol = snapshot.symbol;

  if (signal.type == SignalType::BUY) {
    int quantity = sizer.calculate_quantity(portfolio, snapshot.close);
    if (quantity <= 0) return std::nullopt;
    order.side = OrderSide::BUY;
    order.quantity = quantity;
  } else if (signal.type == SignalType::SELL) {
    if (portfolio.shares <= 0) {
      return std::nullopt;
    }
    order.side = OrderSide::SELL;
    order.quantity = portfolio.shares;
  } else {
    throw std::runtime_error("Unknown Signal Type");
  }

  return order;
}