#include "../../include/execution/order_manager.hpp"

Order OrderManager::generate_order(const Signal& signal,
                                   const Portfolio& portfolio,
                                   const MarketSnapShot& snapshot,
                                   const PositionSizer& sizer) {
  Order order;
  order.timestamp = snapshot.timestamp;
  order.symbol = snapshot.symbol;

  if (signal.type == SignalType::BUY) {
    order.side = OrderSide::BUY;
    int quantity = sizer.calculate_quantity(portfolio, snapshot.close);
    order.quantity = quantity;
  } else if (signal.type == SignalType::SELL) {
    order.side = OrderSide::SELL;
    order.quantity = portfolio.shares;
  } else {
    order.side = OrderSide::HOLD;
    order.quantity = 0;
  }

  return order;
}