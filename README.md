# MarketForge

## Copyright & Usage

© 2026 Qi Tang. All rights reserved.

For research and educational presentation only.

Copying, modification, and reuse for learning and research are permitted. Please retain appropriate attribution and do not redistribute or present this project, or substantial portions of its source code, as your own original work.

### 版权与使用说明

© 2026 Qi Tang. 保留所有权利。

本项目仅用于研究与教育展示。

允许出于学习和研究目的复制、修改和复用代码，但请保留适当署名，不得将本项目或其中较大比例的源代码冒充为自己的原创成果重新发布或展示。

## Project Summary

MarketForge is a quantitative research and backtesting project that combines market-data processing, strategy research, execution simulation, portfolio accounting, performance analysis, and result reporting. The project is organized as a modular workflow in which Python handles data acquisition and preprocessing, while the core quantitative strategy and backtesting engine, **QuantLab 2.0**, is implemented in modern C++20.

### C++ / QuantLab 2.0

The C++ engine is designed around clear separation of responsibilities and reusable interfaces. Market data is loaded into a centralized `MarketData` container and exposed to strategies through lightweight read-only `std::span<const PriceBar>` views, avoiding unnecessary data copying during backtests.

The trading pipeline separates strategy logic, position sizing, order generation, order validation, execution modeling, trade execution, portfolio accounting, and performance analysis into independent components. This allows different strategies and execution rules to reuse the same backtesting infrastructure.

Implemented capabilities include:

- Multi-symbol and multi-timeframe backtesting for daily and 5-minute A-share data.
- Strategy abstraction through a common `Strategy` interface.
- Moving Average Crossover, Bollinger Breakout, and RSI Mean-Reversion strategies.
- Reusable technical indicators and configurable strategy parameters.
- Position sizing, executable-order validation, A-share lot-size handling, slippage simulation, commission, and sell-side stamp duty.
- Portfolio cash, position, market value, and equity tracking on every market bar.
- Structured `BacktestResult`, trade history, equity history, and completed-trade analysis.
- Portfolio and trade-level metrics including total/annualized return, volatility, Sharpe, Sortino, Calmar, maximum drawdown, win rate, profit-loss ratio, and win/loss statistics.
- Batch parameter sweeps, best-versus-second-best parameter sensitivity analysis, and structured report generation.
- Export of the best strategy equity history, trade history, buy-and-hold benchmark, and drawdown series for visualization.
- Runtime optimization by operating indicators directly on `std::span` data views and removing repeated full-history conversions from the strategy hot path.

### Python Data Pipeline

Python scripts support the surrounding research workflow, including market-data acquisition, cleaning and validation, daily and 5-minute data preparation, financial-statement processing, fundamental-factor construction, valuation and trading-activity analysis, price-limit event analysis, integrated stock profiling, and conversion of analysis outputs into visualization-ready datasets.

## 项目总结

MarketForge 是一个面向量化研究与回测的综合项目，覆盖市场数据处理、策略研究、交易执行模拟、账户管理、绩效分析和结果输出。项目采用模块化设计：Python 主要负责数据获取、清洗和分析预处理，核心量化策略与回测引擎 **QuantLab 2.0** 则使用现代 C++20 实现。

### C++ / QuantLab 2.0

C++ 引擎强调职责分离、接口复用与运行效率。市场数据由统一的 `MarketData` 容器管理，策略通过轻量级只读 `std::span<const PriceBar>` 访问历史数据，避免回测过程中不必要的数据复制。

交易流程将策略逻辑、仓位计算、订单生成、订单验证、执行模型、成交生成、Portfolio 更新和绩效分析拆分为独立模块，使不同策略能够复用同一套回测基础设施。

主要实现功能包括：

- 支持多股票、多时间频率（日线与 5 分钟）的批量回测。
- 通过统一 `Strategy` 接口实现策略多态。
- 实现双均线交叉、布林带突破和 RSI 均值回归策略。
- 提供可复用技术指标和可配置策略参数。
- 实现仓位管理、订单可执行性验证、A 股整手规则、滑点、佣金和卖出印花税模拟。
- 在每个市场 bar 上记录现金、持仓、市值和权益变化。
- 使用结构化 `BacktestResult` 保存交易记录、权益历史和完整交易周期。
- 计算总收益率、年化收益率、波动率、Sharpe、Sortino、Calmar、最大回撤、胜率、盈亏比及各类胜负交易统计。
- 支持批量参数扫描、最优与次优参数敏感性分析以及结构化报告输出。
- 导出最优参数组合的权益曲线、交易历史、Buy & Hold 基准和回撤序列，用于后续可视化。
- 通过直接在 `std::span` 上计算指标，移除策略热路径中的重复历史数据转换，大幅提升分钟级批量回测效率。

### Python 数据脚本

Python 脚本负责项目外围的数据与研究流程，包括行情数据获取、清洗与质量检查、日线与 5 分钟数据处理、财务报表整理、基本面因子构建、估值与交易活跃度分析、涨跌停事件分析、股票综合画像，以及将分析结果转换为便于可视化使用的数据格式。


## DEVELOPMENT LOG

### Project Status
### Phase 1: Environment Setup & Data Fetching and Processing Pipeline

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

### Project Status
### Phase 2: Minute-Level Data Fetching and Processing Pipeline & Interactive K-Line Website

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

### Project Status
### Phase 3: C++ Quantitative Strategy and Backtesting Engine Development

### Quant Engine Framework Construction

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

============================================================================

## Trading Execution Framework Development

### Aug 10, 2026: Order Validation and Execution Model Refactoring

- Investigated and resolved negative cash issue during full-position BUY execution.
- Identified that execution price slippage and transaction fees caused the actual trading cost to exceed the estimated order value.

- Introduced `OrderValidator` module to separate order generation from order feasibility checking.
  - Validates whether an order can be executed under current portfolio constraints.
  - Adjusts order quantity according to available cash and A-share trading lot size.
  - Prevents invalid BUY orders caused by insufficient capital.
  - Adjusts SELL orders according to available positions.

- Introduced `ExecutionQuote` data structure.
  - Represents pre-trade execution estimation.
  - Stores:
    - Execution price
    - Trade value
    - Commission
    - Stamp duty
    - Slippage cost
    - Total transaction fee

- Introduced `ExecutionModel`.
  - Centralized execution price simulation and transaction cost estimation.
  - Removed duplicated cost calculation logic from execution-related modules.
  - Provides a single source of truth for execution cost estimation.

- Refactored `ExecutionEngine`.
  - Simplified execution responsibility.
  - ExecutionEngine now converts validated orders and execution quotes into final Trade records.
  - Removed responsibility for calculating transaction costs.

---

### Architecture Improvement

#### Before:
```text
Order
|
↓
ExecutionEngine
|
├── Execution Price Calculation
├── Commission Calculation
├── Stamp Duty Calculation
├── Slippage Calculation
|
↓
Trade
```

#### After

```teSignal
↓
OrderManager
↓
Order
↓
OrderValidator
↓
Valid Order
↓
ExecutionModel
↓
ExecutionQuote
↓
ExecutionEngine
↓
Trade
↓
Portfolio
```

### Testing:
```text
Successfully tested the complete BUY execution workflow:

Initial Portfolio:
Cash: 100000
Shares: 0

Original Order:
Side: BUY
Quantity: 10000

After validation:
Adjusted Quantity: 9900

Execution Result:
Execution Price: 10.005
Commission: 49.5247
Stamp Duty: 0
Slippage Cost: 49.5

Portfolio Update:
Cash: 900.975
Market Value: 99000
Equity: 99901
Shares: 9900

The result confirms:

- Transaction costs are correctly applied.
- Full-position trading does not create negative cash.
- Execution price and cost calculations are consistent between validation and execution.
```
---
## Design Reflection

A seemingly simple negative cash issue revealed the importance of separating position sizing, order validation, execution modeling, and portfolio management.

This refactoring improved the architecture by ensuring:

- PositionSizer determines intended position size.
- OrderValidator ensures orders are executable.
- ExecutionModel provides consistent execution estimation.
- ExecutionEngine generates final trade records.
- Portfolio maintains account state.

============================================================================

### Aug 11, 2026: Completed Backtester Integration and End-to-End Trading Simulation

#### Optimized Strategy Data Interface with std::span
- Replaced the previous historical data copying approach in `Backtester` with `std::span<const PriceBar>`.
- Removed unnecessary `PriceFrame` duplication during each backtest iteration.
- Updated the `Strategy` interface and `MovingAverageStrategy` implementation to accept read-only market data views.
Design improvement:
- `PriceFrame` remains responsible for owning market data.
- `std::span<const PriceBar>` provides a lightweight, non-owning view for strategy calculation.
- Improved memory efficiency while maintaining clear ownership boundaries.

#### Updated MovingAverageStrategy for std::span Support
- Modified `MovingAverageStrategy::generate_signal()` to process `std::span<const PriceBar>`.
- Preserved SMA crossover logic while removing unnecessary data copying.
- Verified that the strategy correctly identifies crossover events.


### Testing:
- Created custom price data containing a downward trend followed by a recovery phase.
- Confirmed:
  - Insufficient history returns `HOLD`.
  - Golden-cross events correctly generate `BUY` signals.

Backtester now supports:

- Iterating through historical market data.
- Passing historical data views to strategies.
- Generating orders based on strategy signals.
- Validating and adjusting orders according to account constraints.
- Executing trades with transaction costs.
- Updating portfolio positions and market value.

##### Performed Full End-to-End Backtest Validation

Successfully tested a complete BUY transaction.

Test scenario:

Initial Cash: 100000
Strategy: Moving Average Crossover
Signal: BUY
Market Price: 20


Order process:
Original Quantity: 5000
Adjusted Quantity: 4900


Execution result:
Execution Price: 20.01
Commission: 49.0245
Slippage Cost: 49


Portfolio update:
Cash: 1901.98
Shares: 4900
Market Value: 98000
Equity: 99902


Validated:

- Correct signal generation.
- Correct order adjustment.
- Correct transaction cost calculation.
- Correct portfolio accounting after execution.

---

### Fixed C++20 Development Environment Configuration

Resolved VSCode IntelliSense compatibility issue.

Updated configuration:
Compiler:
gcc → g++

Language Standard:
C17 → C++20

Enabled proper recognition of modern C++ features including:
```cpp
std::span<T>
```


### Aug 11, 2026: MarketData Structure and Real Market Data Integration

- Designed and implemented `MarketData` structure to support multiple symbols and multiple time frequencies.

  - Used nested `unordered_map` structure:
    - Symbol → TimeFrame → PriceFrame
  - Added `TimeFrameHash` to support using `enum class TimeFrame` as `unordered_map` key.
  - Added `TimeFrameData` alias to improve readability.

- Implemented `MarketData` data access interface.

  - Added `add_data()` for storing loaded market data.
  - Used move semantics to transfer ownership of `PriceFrame` into `MarketData`.
  - Added read-only `get_data()` interface returning `const PriceFrame&`.
  - Used iterator-based lookup to avoid unnecessary data insertion during retrieval.

- Connected CSV data loading pipeline with `MarketData` and `Backtester`.

  - Replaced manually constructed `PriceFrame` test data with real historical market data loaded from CSV files.
  - Completed data flow:
    - CSV
    - DataLoader
    - PriceFrame
    - MarketData
    - Backtester

- Tested Moving Average Crossover Strategy using real A-share historical data.

  - Successfully generated BUY and SELL signals from loaded market data.
  - Verified complete order lifecycle:
    - Signal generation
    - Order creation
    - Order validation
    - Trade execution
    - Portfolio update

- Fixed `OrderValidator` SELL validation issue.

  - Identified incorrect condition in SELL branch:
  
### Testing:
```text
Example backtest result:
Order Side: BUY
Original Quantity: 59500
Adjusted Quantity: 59400

Execution Price: 1.68084
Commission: 49.9209
Stamp Duty: 0
Slippage Cost: 49.896

Shares: 59400
Order Side: SELL
Quantity: 59400

Execution Price: 1.61919
Commission: 48.0899
Stamp Duty: 48.0899
Slippage Cost: 48.114

Shares: 0
...
```

============================================================================

### Aug 12, 2026: Backtest Result Recording and Performance Analysis Integration

- Introduced `BacktestResult` to store structured outputs generated during backtesting.
  - Added trade history recording.
  - Added equity history recording.
  - Replaced terminal-only backtest observation with reusable result data.

- Added `EquityPoint` structure to record portfolio state at each market bar.
  - Stores:
    - Timestamp
    - Cash
    - Shares
    - Market value
    - Equity
  - Updated portfolio market value on every bar, including periods without trade execution.
  - Ensured equity history correctly reflects mark-to-market portfolio changes during HOLD periods.

- Refactored `BackTester::run()` to return `BacktestResult`.
  -  Records each executed `Trade`.
  - Records portfolio equity state for every historical bar.
  - Prepared backtest results for downstream performance analysis and report generation.

- Resolved missing symbol propagation in the trading pipeline.
  - Removed `symbol` from `PriceBar` because symbol information belongs to the market-data context rather than individual OHLCV bars.
  - Passed symbol directly into `BackTester::run()`.
  - Forwarded symbol from Backtester to `OrderManager`.
  - Verified symbol propagation through:
    - Order
    - Validated Order
    - Trade

- Refactored time-series return handling.
  - Reused existing `TimeSeries` infrastructure for portfolio equity analysis.
  - Added equity-history extraction from `BacktestResult`.
  - Generalized `simple_return()` to operate on arbitrary value series rather than price-only inputs.
  - Preserved timestamps and NaN positions during time-series transformations.

- Revised NaN handling policy.
  - Removed unnecessary `drop_nan()` calls from time-series transformation functions.
  - Preserved original time structure when calculating returns and drawdowns.
  - Kept NaN filtering inside statistical aggregation functions such as:

    - `mean()`
    - `var()`
    - `stdev()`
    - `max()`
    - `min()`
  - Added empty-series protection to `max()` and `min()`.

- Integrated portfolio-level performance metrics with `BacktestResult`.
  - Implemented:
    - Total Return
    - Annualized Return
    - Annualized Volatility
    - Sharpe Ratio
    - Maximum Drawdown
  - Calculated strategy returns from portfolio equity instead of underlying asset prices.
  - Generalized period-related naming to support both daily and intraday backtests.


### Aug 12, 2026: Closed Trade Analysis and Performance Module Completion

- Introduced `ClosedTrade` and `ClosedTradeHistory` to represent completed BUY-to-SELL trading cycles.

  - Added extraction logic to pair entry and exit trades from `BacktestResult::trades`.
  - Calculated realized PnL and return rate for each completed trade.
  - Kept unfinished open positions excluded from closed-trade statistics.
  - Reused execution prices directly so slippage costs were not deducted twice.

- Extended `PerformanceAnalyzer` with trade-level performance statistics based on `ClosedTradeHistory`.

  - Added win/loss statistics, profit-loss ratio, and maximum profit/loss analysis.
  - Used STL algorithms such as `std::max_element` and `std::min_element` with custom comparators for ClosedTrade lookup.
  - Added defensive handling for empty histories and strategies containing no winning or losing trades.

- Added Sortino Ratio and Calmar Ratio to complete the required risk-adjusted performance metrics.

  - Sortino Ratio measures return relative to downside volatility.
  - Calmar Ratio compares annualized return against maximum drawdown.

- Completed end-to-end integration testing of the performance analysis pipeline:

```text
BackTester
    ↓
BacktestResult
    ├── Trade History
    └── Equity History
            ↓
ClosedTradeHistory
            ↓
PerformanceAnalyzer
```

- Identified an equity-history recording issue during performance testing.

  - `BackTester` previously used `continue` when no order was generated.
  - HOLD periods therefore skipped mark-to-market updates and equity recording.
  - A 243-bar backtest initially produced only 51 equity records, causing annualized performance metrics to be significantly overstated.

- Refactored the Backtester loop so market value and equity are updated and recorded for every market bar regardless of whether an order is generated or executed.

  - Verified that 243 price bars now produce 243 equity-history records.
  - Re-tested annualized return, volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio, and maximum drawdown after the correction.
  - Confirmed that trade-level statistics remained unchanged because the fix affected portfolio mark-to-market recording rather than actual trade execution.

- Completed and validated the Performance module with both portfolio-level and trade-level metrics.

- Improved performance output formatting for readability.

  - percentage metrics are displayed in `%` form
  - ratios are displayed as concise decimal values
  - PnL statistics use fixed decimal precision
  - prepared performance results for cleaner terminal and future report output


### Aug 12, 2026: Bollinger Breakout Strategy Implementation and Validation

- Added `BollingerStrategy` as the second concrete strategy derived from the common `Strategy` interface.

- Refactored the existing SMA calculation from `MovingAverageStrategy` into the indicator layer so it can be reused by multiple strategies.

- Added rolling standard deviation calculation for Bollinger Band construction.

  - used population standard deviation for rolling price windows
  - preserved the original rolling-window structure when handling price data
  - added parameter and insufficient-data validation

- Implemented Bollinger breakout signal generation using historical price data through `std::span`.

  - constructed upper and lower Bollinger Bands from rolling SMA and standard deviation
  - generated BUY signals when price crossed above the upper band
  - generated SELL signals when price crossed below the lower band
  - used crossing conditions instead of continuous above/below-band conditions to avoid repeated signals

- Integrated `BollingerStrategy` into the existing backtesting pipeline without modifying the Backtester, execution, portfolio, or performance components.

- Tested the strategy using real A-share daily historical data.

  - confirmed 243 price bars produced 243 equity-history records
  - verified that the strategy generated two completed BUY-to-SELL trading cycles
  - inspected individual entry/exit timestamps, prices, quantities, realized PnL, and return rates
  - confirmed that closed-trade details matched the aggregated win/loss statistics

- Validated the resulting portfolio-level and trade-level performance metrics, including return, volatility, Sharpe Ratio, Sortino Ratio, Calmar Ratio, maximum drawdown, win rate, and profit-loss statistics.

- Confirmed that the strategy abstraction supports replacing the trading strategy while reusing the complete order, execution, portfolio, backtesting, and performance-analysis infrastructure.

============================================================================

### Aug 13, 2026: RSI Strategy Integration and Parameter Sweep Framework

- Added RSI calculation as a reusable indicator function.

  - implemented average gain and average loss calculation over a rolling window
  - handled RSI edge cases for fully rising, fully falling, and flat price series
  - validated the implementation with manually constructed test cases
  - confirmed expected RSI outputs of 100, 0, 50, and 66.67 for representative scenarios

- Added `RSIStrategy` as the third concrete strategy derived from the common `Strategy` interface.

  - added configurable RSI window, oversold threshold, overbought threshold, and selected price field
  - implemented crossing-based mean-reversion signals
  - generated BUY signals when RSI recovered above the oversold threshold
  - generated SELL signals when RSI fell back below the overbought threshold
  - added parameter and minimum-history validation

- Tested `RSIStrategy` with real A-share daily historical data.

  - verified complete backtest execution through order generation, validation, execution, portfolio updates, and performance analysis
  - inspected closed-trade details including entry/exit timestamps, prices, quantities, PnL, and return rates
  - confirmed trade-level statistics matched the underlying closed trades
  - confirmed that 243 market bars produced 243 equity-history records

- Extended the `Strategy` abstraction with strategy metadata.

  - added virtual strategy name and parameter-description interfaces
  - allowed each concrete strategy to report its own strategy name and parameter configuration
  - removed the need for the backtest runner to manually identify individual strategy types

- Added `BacktestSummary` to represent one complete backtest experiment.

  - stored symbol, timeframe, strategy name, parameter description, portfolio-level metrics, and trade-level statistics
  - created a common result format for parameter comparison and future CSV export

- Added a reusable `run_backtest()` function to execute one independent strategy experiment.

  - initialized a fresh portfolio for every run to prevent state leakage between parameter combinations
  - reused the existing strategy, order, execution, portfolio, backtesting, and performance components
  - converted each completed run into a `BacktestSummary`

- Added timeframe-aware annualization support.

  - mapped each `TimeFrame` to its corresponding `periods_per_year`
  - kept `PerformanceAnalyzer` stateless by passing annualization frequency explicitly

- Added parameter configurations for Moving Average, Bollinger, and RSI strategies.

  - executed multiple parameter combinations for each strategy
  - stored all experiment results in `std::vector<BacktestSummary>`

- Added formatted summary output for parameter-sweep results.

  - displayed returns, volatility, drawdown, risk-adjusted ratios, trade counts, win rate, and profit-loss ratio
  - converted return-based metrics into percentage form for readability
  - verified that all nine strategy-parameter combinations executed independently and produced distinct performance results

- Confirmed that the backtesting engine now supports batch strategy experiments through a shared execution pipeline, preparing the system for parameter ranking, best-versus-second-best comparison, multi-symbol testing, multi-timeframe testing, and CSV result export.


### Aug 13, 2026: Batch Backtesting Integration and Runtime Optimization

- Completed the multi-parameter execution workflow in `main()` for Moving Average, Bollinger, and RSI strategies.

- Extended the backtesting pipeline to support multiple symbols and both daily and 5-minute timeframes.

- Integrated `MarketData` into the batch workflow by loading market data into the centralized container and retrieving `PriceFrame` objects by symbol and timeframe.

- Improved `DataLoader` to support different CSV schemas by resolving OHLCV fields from column headers instead of relying on fixed column positions.

- Simplified parameter sensitivity analysis so that each analysis operates directly on summaries from a single strategy group.

- Updated `.clang-format` to improve code layout consistency and overall readability.

- Diagnosed and resolved a major runtime performance issue during batch backtesting:
  - Observed that Moving Average and Bollinger backtests completed within fractions of a second, while RSI backtests became significantly slower as more data was processed.
  - Added runtime measurements and progress checks to isolate the bottleneck to the RSI signal-generation path.
  - Identified that strategy calculations were repeatedly converting the entire historical `std::span<const PriceBar>` into a new `TimeSeries` through `extract_price_series()` on every market bar.
  - This introduced unnecessary full-history traversal, dynamic allocation, and repeated construction of `TimeSeriesPoint` objects during signal generation.
  - Refactored indicator calculations to operate directly on `std::span<const PriceBar>` and access the selected price field through the `PriceBar` member pointer.
  - Removed the redundant intermediate `TimeSeries` construction from the strategy hot path while preserving the same indicator and signal logic.
  - Reduced unnecessary data copying and simplified the data flow from `PriceFrame` to strategy indicators.
  - After optimization, a single strategy-parameter backtest over approximately 23,000 five-minute bars completes in about 94 ms.
  - Confirmed that the optimized implementation is fast enough to support the full multi-symbol, multi-timeframe parameter sweep.

============================================================================

### Aug 14, 2026: QuantLab 2.0 Report Pipeline and Finalization

- Completed formatted output functions for both `BacktestSummary` and `ParameterSensitivity` using `std::ostream` and `std::iomanip`.

- Improved strategy parameter formatting to remove unnecessary decimal digits and produce cleaner human-readable reports.

- Integrated `std::ofstream` output into the batch backtesting workflow so backtest summaries and parameter sensitivity results are automatically written to report files.

- Added automatic report directory creation using `std::filesystem`.

- Organized generated reports into two main categories:
  - `report/backtest_summary/`
  - `report/strategy_parameter_sensitivity/`

- Added symbol-level subdirectories under both report categories, keeping the six strategy/timeframe reports for each stock together and making large batch results easier to inspect.

- Reused a common report-writing workflow across Moving Average, Bollinger, and RSI strategies to avoid duplicated file-output logic.

- Successfully completed and validated the full multi-symbol, multi-timeframe, multi-strategy parameter sweep and report generation pipeline.

- Finalized QuantLab 2.0 with an end-to-end workflow covering market data loading, strategy execution, transaction simulation, portfolio accounting, performance analysis, parameter sensitivity analysis, runtime optimization, and structured result reporting.


### Aug 14, 2026: Best Strategy History Export

- Refactored the backtesting workflow to preserve both `BacktestResult` and `BacktestSummary` for each parameter configuration.

- Updated parameter sensitivity analysis to retain the complete backtest history of the best-performing parameter combination.

- Added CSV output for the best strategy equity history, including portfolio cash, shares, market value, and equity.

- Added CSV output for the best strategy trade history, including execution price, quantity, commission, stamp duty, and slippage cost.

- Added buy-and-hold benchmark equity and drawdown time series for visualization and further analysis.

- Organized best equity and trade histories by symbol, timeframe, and strategy.

- Verified that all existing backtest summary and parameter sensitivity functionality remained unchanged after the refactor.

============================================================================

```text
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          38           2351            195           7938
C++                             16            348              1           1235
Markdown                         1            318              0           1099
C/C++ Header                    28            177              0            566
Text                             1             54              0            192
CMake                            1              6              0             43
JSON                             2              0              0             20
YAML                             1              6              0             19
Jupyter Notebook                 1              0             89             17
-------------------------------------------------------------------------------
SUM:                            89           3260            285          11129
-------------------------------------------------------------------------------
```