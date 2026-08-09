# MarketForge

MarketForge is a quantitative research platform designed for financial data acquisition, storage, cleaning, analysis, strategy development, and backtesting.

## Initial Data Sources

- AKShare
- A-share market data
- ETHUSDT market data

## Project Status
## Phase 1: Environment Setup & Data Fetching and Processing Pipeline

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

## Project Status
## Phase 2: Minute-Level Data Fetching and Processing Pipeline & Interactive K-Line Website

### July 27, 2026 — Minute-Level Data Interface Test

- Created two new general folder, market_data_pipeline and minute_kline, to pack the work of week_1 and week_2 respectively, aiming to show a more clear project structure.
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
- implemented new missing value inspection function in src/inspect_minute_data.py
- No missing values in all cleaned stock minute data, the data quality is good.

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

============================================================================

### August 3, 2026 — ETHUSDT Data Pipeline and K-Line Website Integration

- Reviewed BaoStock's financial-data coverage and compared its available indicators with the listed-company financial-statement field dictionary.
- Confirmed that BaoStock does not support cryptocurrency market data.
- Switched to the Binance.US public K-line API to retrieve ETHUSDT 5-minute spot data.
- Implemented paginated requests using `startTime` and `endTime` to collect approximately two years of historical data.
- Cleaned the ETHUSDT dataset by converting datetime and numeric fields, removing invalid or duplicated records, validating OHLC relationships, and checking nonnegative trading values.
- Preserved valid zero-volume K-lines because they represent intervals without trades rather than missing data.
- Converted the cleaned CSV data into a web-ready JSON format.
- Integrated ETHUSDT into the existing interactive K-line website alongside the 16 A-share stocks.
- Added a dedicated `Spot` price type for ETHUSDT while restricting A-share stocks to `QFQ` and `Unadjusted`.
- Fixed an incorrect Unix timestamp conversion that caused ETHUSDT dates to appear in 1970 and reduced the number of unique displayed bars.
- Limited the default ETHUSDT web dataset to the latest 20,000 bars to improve loading and rendering performance.
- Verified stock selection, adjustment-type controls, candlestick display, volume display, crosshair information, zooming, and dragging.

**Data flow:**

```text
Binance.US API
→ Two-year 5-minute ETHUSDT data
→ CSV storage
→ Data cleaning and validation
→ JSON conversion
→ Interactive K-line website
```

Current website coverage:

16 A-share stocks with QFQ and unadjusted prices
ETHUSDT with spot prices
Candlestick and volume charts
Asset and price-type selection
Crosshair OHLCV information
Zoom, drag, and reset-view functions

============================================================================

### August 5, 2026 — Hong Kong Financial Statement Data Pipeline

- Researched available interfaces for Hong Kong-listed company financial statements.
- Confirmed that AKShare can retrieve detailed annual balance sheets, income statements, and cash flow statements through `stock_financial_hk_report_em`.
- Tested the interface using Hong Kong stock `02180` and verified that it returned continuous multi-year financial data with standardized item codes, item names, report dates, and reported amounts.
- Evaluated data coverage:
  - Balance sheet: 10 annual periods and 45 unique financial items.
  - Income statement: 10 annual periods and 29 unique financial items.
  - Cash flow statement: 10 annual periods and 50 unique financial items.
- Created a new `fundamentals` module parallel to `minute_kline` for financial-statement collection, cleaning, storage, and future fundamental analysis.
- Implemented batch retrieval for the selected Hong Kong stocks:
  - `02180`
  - `08365`
  - `08462`
  - `02076`
  - `06100`
  - `06919`
  - `09669`
- Retrieved annual balance sheets, income statements, and cash flow statements for each stock.
- Stored each statement separately by stock code and statement type.
- Preserved the original AKShare results in the `raw` directory.
- Standardized cleaned financial data into a long-table structure containing:
  - Security identifier
  - Stock code and name
  - Organization code
  - Statement type
  - Reporting currency
  - Report date and start date
  - Fiscal year
  - Financial item code and name
  - Reported amount
- Cleaned the data by:
  - Stripping whitespace from column names.
  - Standardizing different report-date fields.
  - Converting report dates and start dates to datetime values.
  - Converting reported amounts to numeric values.
  - Renaming source fields into consistent English column names.
  - Removing rows with missing key identifiers.
  - Removing duplicated stock, statement, report-date, and item-code records.
  - Sorting records by report date and financial item code.
- Retained missing financial amounts where the reporting item itself was valid, since missing values may represent non-applicable or undisclosed items rather than invalid records.
- Added a `currency` column using a stock-to-currency mapping, allowing reporting currencies to be managed consistently and extended for future stocks.

**Outputs:**

```text
fundamentals/
├── src/
│   └── fetch_clean_financial_reports.py
└── data/
    ├── cleaned/
    │   └── hk/
    │       ├── balance_sheet/
    │       │     ├── 02180_balance_sheet_annual.csv
    │       │     └── ...
    │       ├── cash_flow_statement/
    │       │     ├── 02180_cash_flow_statement_annual.csv
    │       │     └── ...
    │       └── income_statement/
    │             ├── 02180_income_statement_annual.csv
    │             └── ...
    └── raw/
        └── hk/
            ├── balance_sheet/
            │     ├── 02180_balance_sheet_annual.csv
            │     └── ...
            ├── cash_flow_statement/
            │     ├── 02180_cash_flow_statement_annual.csv
            │     └── ...
            └── income_statement/
                  ├── 02180_income_statement_annual.csv
                  └── ...
```
============================================================================

### August 6, 2026 — A-Share Financial Statements and Project Structure Optimization

- Implemented a batch financial-statement pipeline for 16 A-share stocks.
- Added retrieval of complete historical:
  - Balance sheets
  - Income statements
  - Cash flow statements
- Used AKShare report-period interfaces to obtain annual, semiannual, first-quarter, and third-quarter financial data.
- Stored both raw and cleaned financial statements by stock code and statement type.
- Standardized stock codes, report dates, statement types, currency fields, and common identification columns.
- Preserved all available financial-statement fields while removing invalid key records and duplicated report entries.
- Added fetch summaries containing retrieval status, row count, column count, report-period coverage, missing-cell count, and report-date range.
- Optimized the directory structure of `market_data_pipeline` to make market-data files easier to classify and maintain.
- Improved the output paths and processing logic in:
  - `fetch_stock_data.py`
  - `inspect_stock_data.py`
  - `clean_stock_data.py`
- Refactored related algorithms and file-handling logic to improve code readability, consistency, and maintainability.
- Reorganized generated data into clearer raw, cleaned, inspection, and summary categories.
- Moved all fundamental-data-related files and modules from `market_data_pipeline` into the independent `fundamentals` directory.
- Separated market-data processing from financial-statement processing, resulting in a clearer and more modular overall project structure.

**Outputs:**

```text
fundamentals/
├── src/
│   └── fetch_a_financial_reports.py
│
└── data/
    ├── raw/
    │   └── a_share/
    │       ├── balance_sheet/
    │       ├── income_statement/
    │       ├── cash_flow_statement/
    │       └── stock_fundamental_summary/
    │
    ├── cleaned/
    │   └── a_share/
    │       ├── balance_sheet/
    │       ├── income_statement/
    │       └── cash_flow_statement/
    │
    └── summary/
        └── a_share_financial_fetch_summary.csv
```

============================================================================

### August 6, 2026: Fundamental Data Inspection and Factor Construction

- Inspected the A-share financial statement data, including the balance sheet, income statement, and cash flow statement.
- Checked available columns and identified the required financial fields.
- Created a field mapping for revenue, net profit, assets, liabilities, equity, and operating cash flow.
- Cleaned and standardized the financial statement data.
- Preserved `report_date` and `notice_date` for future point-in-time analysis.
- Built nine fundamental factors:
  - Revenue growth
  - Parent net profit growth
  - Gross margin
  - Net margin
  - ROE
  - Debt-to-asset ratio
  - Operating cash flow to net profit
  - Current ratio
  - Total asset growth
- Generated individual factor files for all 16 A-share companies.
- Combined all individual results into one fundamental factor dataset.
- Saved the outputs under the `fundamentals/data/factors/a_share/` directory.


**Outputs:**

```text
fundamentals/
├── data/
│   └── factors
│       └── a_share
│           ├── individual
│           │   ├── sh600231_fundamental_factors.csv
│           │   └── ...
│           └── a_share_fundamental_factors.csv          
└── src/
    ├── build_a_fundamental_factors.py
    └── inspect_a_factor_fields.py
```

###  August 7, 2026: Valuation and Limit Event Analysis

- Collected historical A-share valuation data, including:
  - PE (TTM)
  - Static PE
  - PB
  - Total market capitalization
- Cleaned and filtered valuation data for the 2025 analysis period.
- Generated individual and combined valuation datasets for all 16 stocks.
- Tested historical fund flow data interfaces and added retry handling for network failures.
- Identified connectivity issues with the Eastmoney fund flow endpoint and treated fund flow data as an optional data source.
- Designed a simplified price-limit rule:
  - ChiNext stocks (`300xxx`): 20%
  - Other sample stocks: 10%
  - Historical ST status temporarily excluded
- Implemented daily limit event detection using unadjusted price data.
- Identified:
  - Limit-up events
  - One-word limit-up events
  - Failed limit-up events
  - Consecutive limit-up events
- Calculated post-limit performance:
  - Next-day open return
  - Next-day close return
  - 3-day return
  - 5-day return
- Added 5-day maximum return and drawdown measurements.
- Added volume and turnover-related features for limit events.
- Tested the pipeline on `sz002067` and verified the event detection results.
- Extended the analysis pipeline to process all 16 A-share stocks.
- Generated individual event data, combined event data, and stock-level summary datasets.

**Outputs:**

```text
market_data_pipeline/
├── src/
│   ├── analyze_all_limit_events.py
│   └── fetch_stock_valuation.py
│
└── data/
    └── analysis/
        └── limit_analysis/
            ├── daily/
            │     ├── sh600231_limit_analysis.csv
            │     └── ...
            ├── events/
            │     ├── sh600231_limit_events.csv
            │     └── ...
            ├── individual/
            │     ├── sh600231_limit_analysis.csv
            │     └── ...
            ├── summary/
            │     ├── sh600231_limit_summary.csv
            │     └── ...
            ├── combined_limit_events.csv
            ├── combined_limit_summary.csv
            ├── limit_summary.csv
            └── processing_summary.csv
```

###  August 7, 2026: Activity Analysis Module

- Implemented stock activity analysis module to evaluate trading behavior and market activity characteristics based on historical price and volume data.
- Developed activity analysis scripts:
  - `analyze_stock_activity.py`
  - `analyze_consolidation_patterns.py`
- Implemented individual stock activity analysis:
  - Generated activity analysis results for each stock.
  - Evaluated price-volume behavior and trading activity characteristics.
  - Saved individual analysis outputs.
- Implemented activity summary generation:
  - Generated summarized activity profiles for each stock.
  - Combined individual results into unified summary files.

**Outputs:**

```text
market_data_pipeline/data/analysis/activity_analysis/
├── individual/
│   ├── sz002067_activity_analysis.csv
│   └── ...
├── summary/
│   ├── sz002067_activity_summary.csv
│   └── ...
├── combined_activity_summary.csv
└── processing_summary.csv
market_data_pipeline/data/analysis/activity_analysis/
├── analyze_consolidation_patterns.py
└── analyze_stock_activity.py
```

============================================================================

### August 8, 2026: Activity Analysis Module

- Implemented an integrated stock analysis pipeline to combine fundamental, valuation, and market behavior analysis results into unified stock profiles.
- Built master dataset integration workflow:
  - Combined fundamental factors, valuation metrics, and activity analysis results.
  - Validated input sources before building integrated profiles.
- Generated integrated stock profiles:
  - Merged multiple analysis dimensions for each stock.
  - Created comprehensive stock-level summaries.
- Implemented stock classification:
  - Fundamental scoring.
  - Valuation profile classification.
  - Activity scoring.
  - Limit-up event profiling.
  - Consolidation pattern classification.
  - Market style identification.

**Outputs:**
```text
integrated_analysis/
├── data/
│
├── master/
│   └── a_share_analysis_master_2025.csv
│
├── processed/
│   ├── fundamental_summary_2025.csv
│   ├── valuation_summary_2025.csv
│   ├── stock_profiles_2025.csv
│   └── master_build_validation.csv
│
├── output/
├── reports/
│   └── final_analysis.md
│
└── tables/
    ├── activity_comparison.csv
    ├── fundamental_comparison.csv
    ├── valuation_comparison.csv
    ├── stock_summary_table.csv
    └── integrated_stock_profiles.csv
```

============================================================================

## Project Status
## Phase 2: C++ Quantitative Strategy and Backtesting Engine Development

### August 9, 2026: Strategy and Order Management Framework

- Implemented the initial strategy framework with signal-based decision making.
- Created `Signal` structure to represent trading decisions:
  - BUY
  - SELL
  - HOLD

- Refactored `MovingAverageStrategy` into separate header and source files:
  - Added strategy declaration in `.hpp`
  - Implemented strategy logic in `.cpp`

- Upgraded moving average strategy from simple trend comparison to true crossover detection:
  - Golden Cross → BUY signal
  - Death Cross → SELL signal
  - No crossover → HOLD signal

- Extended `MarketSnapshot` structure to include:
  - Symbol
  - Timestamp
  - Close price
  - Indicator values

- Added position sizing module:
  - Introduced abstract `PositionSizer` interface.
  - Implemented `FullPositionSizer` for full capital allocation.

- Implemented `OrderManager`:
  - Converted trading signals into executable orders.
  - Integrated portfolio information and position sizing logic.
  - Added symbol and timestamp propagation from market data.

### Testing

Successfully tested the complete workflow:
```text
MarketSnapshot
↓
MovingAverageStrategy
↓
Signal
↓
PositionSizer
↓
OrderManager
↓
Order
```

### Current Status

Completed:
- Core trading components
- Strategy interface
- Moving average crossover strategy
- Signal generation
- Position sizing
- Order generation

### Next Step:

- Implement Execution Engine:
  - Convert Order into Trade.
  - Apply slippage.
  - Calculate commission and stamp duty.
  - Connect Trade with Portfolio updates.


### August 9, 2026: Order Management and Trade Execution Framework

- Refactored the order generation workflow by introducing a dedicated position sizing module.
- Added `PositionSizer` abstraction to separate capital allocation logic from order generation.
- Implemented `FullPositionSizer` for full capital allocation strategy.

- Improved `OrderManager` design:
  - Separated signal interpretation, position sizing, and order creation responsibilities.
  - Converted order generation interface to `std::optional<Order>`.
  - Removed unnecessary HOLD orders by returning `std::nullopt` when no trade is required.
  - Improved order generation logic for BUY and SELL signals.

- Implemented `ExecutionEngine` to simulate order execution:
  - Converted `Order` objects into `Trade` objects.
  - Applied slippage model to calculate execution price.
  - Integrated transaction cost calculation:
    - Commission
    - Stamp duty
    - Slippage cost

- Refined transaction cost calculation:
  - Kept trade value based on actual execution price.
  - Updated slippage calculation to measure the difference between market price and execution price.
  - Improved separation between trading price and transaction costs.

### Testing

Successfully validated the workflow:
```text
Signal
↓
OrderManager
↓
Order
↓
ExecutionEngine
↓
Trade
```

### Current Status

Completed:

- Strategy signal generation
- Position sizing framework
- Order management system
- Execution simulation framework

Current trading flow:
```text
Market Data
↓
Strategy
↓
Signal
↓
PositionSizer
↓
OrderManager
↓
Order
↓
ExecutionEngine
↓
Trade
```

### Next Step:

- Integrate Trade with Portfolio.
- Complete account balance and equity updates.
- Build the complete backtesting workflow.