#pragma once

#include <cstddef>
#include <span>

#include "../data/price_bar.hpp"
#include "../data/signal.hpp"
#include "strategy.hpp"

class BollingerStrategy : public Strategy {
 public:
  BollingerStrategy(std::size_t window = 20,
                    double num_std_dev = 2.0,
                    double PriceBar::* price_type = &PriceBar::close);

  Signal generate_signal(
      std::span<const PriceBar> price_history) const override;

 private:
  std::size_t window_;
  double num_std_dev_;
  double PriceBar::* price_type_;
};