# MarketForge

MarketForge is a quantitative research platform designed for financial data acquisition, storage, cleaning, analysis, strategy development, and backtesting.

## Initial Data Sources

- AKShare
- A-share market data
- ETHUSDT market data

## Project Status

Phase 1: Environment setup and data acquisition testing.

## Day 1 Progress
- Set up the project directory, GitHub repository, Conda environment, and VS Code interpreter.
- Installed and verified AKShare and Pandas.
- Tested AKShare historical data acquisition.
- Switched from the Eastmoney interface to the Tencent interface because of    connection issues.

### Separated the workflow into three functions:
-fetch_stock_data()
-store_stock_data()
-fetch_all_stock_data()

### Added empty-data checks, exception handling, and exception chaining with:
-raise RuntimeError(...) from error

## Next Steps
-Complete batch downloading.
-Record successful and failed requests.
-Start data cleaning and validation.