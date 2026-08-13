#pragma once

#include <cstddef>
#include <span>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "strategy.hpp"

class RSIStrategy : public Strategy {
 public:
  RSIStrategy(
      std::size_t window = 14,
      double oversold_threshold = 30,
      double over_bought_threshold = 70,
      double PriceBar::* price_type = &PriceBar::close
  );
  Signal generate_signal(std::span<const PriceBar> price_history) const override;

  std::string name() const override;
  std::string parameters() const override;

 private:
  std::size_t window_;
  double oversold_threshold_;
  double overbought_threshold_;
  double PriceBar::* price_type_;
};