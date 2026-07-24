from data_utils import *
import pandas as pd
import akshare as ak


def fetch_stock_financial_report(stock_code: str) -> pd.DataFrame:

    stock_financial_report = ak.stock_profit_sheet_by_report_em(
        symbol=stock_code.upper(),
    )

    if stock_financial_report.empty:
        raise ValueError(f"No financial report data returned for {stock_code}.")

    return stock_financial_report


stock_financial_report = fetch_stock_financial_report("sz002067")


print(stock_financial_report.columns.tolist())
print(stock_financial_report.head())
