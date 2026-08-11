#pragma once
#include <cstddef>

#include "../data/price_bar.hpp"
#include "../data/time_series.hpp"
#include "strategy.hpp"

class MovingAverageStrategy : public Strategy {
 public:
  MovingAverageStrategy(std::size_t short_window,
                        std::size_t long_window,
                        double PriceBar::* price_type = &PriceBar::close);
  Signal generate_signal(
      std::span<const PriceBar> price_history) const override;

 private:
  std::size_t short_window_;
  std::size_t long_window_;
  double PriceBar::* price_type_;
};