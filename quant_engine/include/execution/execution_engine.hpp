#pragma once

#include "../core/order.hpp"
#include "../core/trade.hpp"
#include "../core/transaction_cost.hpp"

class ExecutionEngine {
 public:
  explicit ExecutionEngine(const TransactionCostModel& cost_model);
  Trade execute(const Order& order, double market_price);

 private:
  TransactionCostModel cost_model_;
};