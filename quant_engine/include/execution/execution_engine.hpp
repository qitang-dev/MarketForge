#pragma once

#include "../core/order.hpp"
#include "../core/trade.hpp"
#include "execution_model.hpp"

class ExecutionEngine {
 public:
  explicit ExecutionEngine(const ExecutionModel& execution_model);
  Trade execute(const Order& valid_order, double market_price);

 private:
  ExecutionModel execution_model_;
};