# MarketForge

MarketForge is a quantitative research platform designed for financial data acquisition, storage, cleaning, analysis, strategy development, and backtesting.

## Initial Data Sources

- AKShare
- A-share market data
- ETHUSDT market data

## Project Status
## Phase 1: Environment setup and data acquisition testing.

## Jul 18 Progress
- Set up the project directory, GitHub repository, Conda environment, and VS Code interpreter.
- Installed and verified AKShare and Pandas.
- Tested AKShare historical data acquisition.
- Switched from the Eastmoney interface to the Tencent interface because of connection issues.
- tx naming rule: add prefix "sh" when stock code starts witn 6
                  add prefix "sz" when stock code starts with 0 or 3

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

===================================================================================================================================================

## Project Status
## Phase 2: Data Acquisition and Inspection.

## Jul 19 Progress
- Loaded target stock codes from `stock_code_list.csv`
- Added Tencent market prefixes (`sz` / `sh`)
- Fetched daily forward-adjusted stock data through AKShare
- Stored raw market data as CSV files in `data/raw/`
- Added exception handling for network, file, and parsing errors
- Recorded batch execution results with success and failure counts
- Built a batch inspection script for all raw datasets
- Generated individual inspection reports containing:
  - file path
  - dataset shape
  - column names
  - data types
  - empty DataFrame status
  - unnamed columns
  - fully empty columns

### Result
All 16 target stock datasets were fetched and stored successfully.
