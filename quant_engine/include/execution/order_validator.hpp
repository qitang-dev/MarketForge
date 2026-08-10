#pragma once

#include <optional>

#include "../core/order.hpp"
#include "../core/portfolio.hpp"
#include "execution_model.hpp"
#include "execution_quote.hpp"

class OrderValidator {
 public:
  OrderValidator(const ExecutionModel& execution_model);
  std::optional<Order> validate_order(const Order& order,
                                      const Portfolio& portfolio,
                                      double market_price) const;

 private:
  ExecutionModel execution_model_;
};