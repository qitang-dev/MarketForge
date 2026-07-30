# MarketForge

MarketForge is a quantitative research platform designed for financial data acquisition, storage, cleaning, analysis, strategy development, and backtesting.

## Initial Data Sources

- AKShare
- A-share market data
- ETHUSDT market data

## Project Status
## Phase 1: Environment Setup and Data Acquisition Testing.

### Jul 18, 2026 - Progress
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

============================================================================

## Project Status
## Phase 2: Data Acquisition and Inspection

### Jul 19, 2026 - Progress
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

============================================================================

## Project Status
## Phase 2: Data Cleaning Pipeline

### Jul 20, 2026 - Progress
A batch data-cleaning pipeline has been completed for all collected A-share datasets.
- Loaded all raw stock CSV files from `data/raw/`
- Standardized column names by removing surrounding whitespace
- Converted the `date` column to Pandas datetime format
- Converted OHLC and trading amount fields to numeric types
- Replaced invalid date and numeric values with missing-value markers
- Removed rows with missing values in required fields
- Removed duplicate trading dates while retaining the latest record
- Sorted all records in chronological order
- Added optional support for using `date` as the DataFrame index
- Preserved the original raw datasets without modification
- Exported all cleaned datasets to `data/cleaned/`

### Result
All target stock datasets were cleaned and stored successfully.

The project now maintains separate data layers:
```
data/
├── raw/       # Original data returned by AKShare
└── cleaned/   # Standardized data ready for analysis
```
============================================================================

### July 22, 2026 — Technical Indicator Calculation

Implemented batch calculation of moving-average indicators for all cleaned stock datasets.

#### Completed Work

- Read cleaned daily stock data from `data/cleaned/`.
- Calculated the following simple moving averages:
  - MA3
  - MA5
  - MA7
  - MA10
  - MA13
  - MA20
  - MA21
- Preserved the original daily OHLC and amount fields.
- Exported indicator-enhanced datasets for each sample stock.
- Added batch-processing status reporting and exception handling.

============================================================================

### July 23, 2026 — Trading Activity Analysis

- Calculated daily return, amplitude, amount change, volume ratio, and 20-day rolling volatility.
- Generated daily activity datasets for all sample stocks.
- Aggregated the results into a cross-sectional activity summary.

**Outputs:**
```
data/activity/
└── {stock_code}_daily_activity.csv

data/analysis/
└── stock_activity_summary.csv
```

### July 23, 2026 — Price Limit Analysis

- Retrieved unadjusted stock data for price-limit analysis.
- Applied simplified 10% limits to Main Board stocks and 20% limits to ChiNext stocks.
- Counted potential limit-up and limit-down events for each stock.

**Output:**
```
data/analysis/
└── stock_price_limit_summary.csv
```

> The model does not separately account for ST stocks, newly listed stocks, special trading rules, or exchange rounding differences.

============================================================================

### July 24, 2026 — Stock Pattern Analysis

- Calculated 20-day rolling highs, lows, average prices, box widths, and MA20 slopes.
- Identified sideways-box, violent-fluctuation, and volume-price-surge patterns.
- Generated a consolidated pattern summary for all sample stocks.

**Outputs:**

```
data/patterns/
└── {stock_code}_daily_patterns.csv

data/analysis/
└── stock_pattern_summary.csv
```

------

### July 24, 2026 — Fundamental Data Summary

- Retrieved financial statement data through AKShare.
- Selected the 2025 annual report for each sample stock.
- Summarized operating revenue, parent net profit, deducted net profit, year-over-year growth, and basic EPS.

**Output:**

```
data/fundamentals/
└── stock_fundamental_summary.csv
```

------

### July 24, 2026 — Stock Valuation Interface Test

- Completed the code for retrieving latest price, dynamic PE, PB, total market value, and free-float market value.
- Tested the `stock_zh_a_spot_em()` interface.
- The upstream server repeatedly closed the connection before returning data.

```
RemoteDisconnected:
Remote end closed connection without response
```

The access and processing code was retained, but no valuation CSV was generated because the third-party endpoint was unavailable.

------

### July 24, 2026 — Cryptocurrency Interface Test

- Tested the `crypto_js_spot()` interface.
- The interface did not include ETHUSDT and returned only a limited set of cryptocurrency pairs.
- Selected BTCUSD as the sample asset and exported the returned market snapshots.

**Output:**

```
data/crypto/
└── btcusd_spot.csv
```

> This module is an interface-availability test rather than a complete cryptocurrency historical-data analysis.

============================================================================

### July 27, 2026 — Minute-Level Data Interface Test

- Created two new general folder, market_data_pipeline and minute_kline, to contain the work for week_1 and week_2 respectively, aiming to show a more clear project structure.
- Tested the Eastmoney `stock_zh_a_hist_min_em()` interface for minute-level stock data.
- The Eastmoney endpoint repeatedly returned `RemoteDisconnected` and could not be accessed successfully.
- Tested the Sina `stock_zh_a_minute()` interface.
- Sina successfully returned 1-minute unadjusted and forward-adjusted data, but the available history covered only approximately 12 days.
- Confirmed that neither tested interface could directly satisfy the requirement for two years of minute-level data.

> The Eastmoney interface was unavailable during testing, while the Sina interface provided insufficient historical coverage.

**Output:**
```text
MARKETFORGE
├── market_data_pipeline
   ├── data
   ├── notebooks
   ├── src

├── minute_kline
   ├── data
   ├── notebooks
   ├── src
      ├── fetch_minute_data.py

```

============================================================================

### July 28, 2026 — BaoStock Minute Data Pipeline

- Continued troubleshooting the Eastmoney connection issue in both WSL and Windows environments.
- Confirmed that the failure was unrelated to the local Python environment, request size, or operating system.
- Investigation indicated that the Eastmoney endpoint was affected by upstream anti-scraping or access-control restrictions.
- Replaced the unavailable interface with BaoStock.
- Successfully retrieved two years of 5-minute market data.
- Collected both unadjusted and forward-adjusted data for all 16 sample stocks.
- Stored each stock dataset as an individual CSV file.

**Outputs:**

```text
data/minute/raw/unadjusted/
├── sz002067_5min_unadjusted_baostock.csv
├── sz002600_5min_unadjusted_baostock.csv
└── ...

data/minute/raw/qfq/
├── sz002067_5min_qfq_baostock.csv
├── sz002600_5min_qfq_baostock.csv
└── ...

BaoStock successfully provided the required two-year minute-level dataset at a 5-minute frequency, including both unadjusted and forward-adjusted prices.
```


============================================================================

### July 29, 2026 - Baostock Raw Minute Data Quality Inspection

- Inspected the number of empty column, the number of unnamed column, the column list, and the data frame shape for all raw stock minute data.
- No empty column or unnamed column was found in each raw stock minute data, and the data quality is good.

**Outputs:**
```text
data/minute/raw/qfq/data_inspection_results
├── sh600231_5min_qfq_inspection_result.txt
├── ...

data/minute/raw/unadjusted/data_inspection_results
├── sh600231_5min_unadjusted_inspection_result.txt
├── ...
```

============================================================================

### July 30, 2026 - Baostock Raw Minute Data Cleaning

- Merged `"date"` and `"time"` into a new column named `"datetime"`. `"datetime"` follows the following format: YYYY/mm/dd/HH/MM/SS
- Kept the following columns: `["datetime","open","high","low","close","volume","amount"]`
- Dropped the following columns : `["date", "time", "code", "adjustflag"]`
- Sorted each raw data frame with the ascending `"datetime"` order.
- Set the index of each raw data frame with `"datetime"`.

**Outputs:**
```text
data/minute/cleaned/qfq
├── cleaned_sh600231_5min_qfq_baostock.csv
├── ...

data/minute/cleaned/unadjusted
├── cleaned_sh600231_5min_unadjusted_baostock.csv
├── ...
```

### July 30, 2026 - K-Line Ploting Test
- Installed mplfinance for k_line ploting
- Using the latest 100 point data in each stock data frame to perform a better visualization.

**Outputs:**
```text
minute_data/figure/qfq
├── sh600231_5min_qfq_kline.png
├── ...

data/minute/cleaned/unadjusted
├── sh600231_5min_unadjusted_kline.png
├── ...
```

### July 30, 2026 — Interactive Minute K-Line Website

- Verified the cleaned 5-minute data by generating a local candlestick chart with Python and `mplfinance`.
- Converted the cleaned QFQ and unadjusted datasets into JSON files for web visualization.
- Built an interactive K-line website using HTML, CSS, JavaScript, and TradingView Lightweight Charts.
- Added support for switching among 16 stocks and between QFQ and unadjusted prices.
- Implemented candlestick, volume, zoom, drag, crosshair, OHLCV display, and reset-view functions.
- Tested the website locally with Python HTTP Server and prepared the static website for Netlify deployment.

**Outputs:**

```text
website/
├── index.html
├── style.css
├── chart.js
└── data/
    ├── qfq/
    └── unadjusted/
```
The website provides an interactive visualization of two years of 5-minute market data for all 16 sample stocks.




