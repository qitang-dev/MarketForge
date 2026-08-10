#pragma once

#include "../core/order.hpp"
#include "../core/transaction_cost.hpp"
#include "execution_quote.hpp"

class ExecutionModel {
 public:
  explicit ExecutionModel(const TransactionCostModel& cost_model);
  ExecutionQuote generate_quote(const Order& order, double market_price) const;

 private:
  TransactionCostModel cost_model_;
};