from pathlib import Path
from data_utils import *

import akshare as ak
import pandas as pd


def fetch_stock_fundamental_summary(
    stock_code: str,
) -> dict:
    stock_financial_report = ak.stock_profit_sheet_by_report_em(
        symbol=stock_code.upper(),
    )

    if stock_financial_report.empty:
        raise ValueError(f"No financial report data returned for {stock_code}.")

    latest_financial_report = stock_financial_report.iloc[0]

    return {
        "stock_code": stock_code,
        "security_name": latest_financial_report["SECURITY_NAME_ABBR"],
        "report_date": latest_financial_report["REPORT_DATE"],
        "report_date_name": latest_financial_report["REPORT_DATE_NAME"],
        "report_type": latest_financial_report["REPORT_TYPE"],
        "notice_date": latest_financial_report["NOTICE_DATE"],
        "operate_income": latest_financial_report["OPERATE_INCOME"],
        "operate_income_yoy": latest_financial_report["OPERATE_INCOME_YOY"],
        "parent_netprofit": latest_financial_report["PARENT_NETPROFIT"],
        "parent_netprofit_yoy": latest_financial_report["PARENT_NETPROFIT_YOY"],
        "deduct_parent_netprofit": latest_financial_report["DEDUCT_PARENT_NETPROFIT"],
        "deduct_parent_netprofit_yoy": latest_financial_report[
            "DEDUCT_PARENT_NETPROFIT_YOY"
        ],
        "basic_eps": latest_financial_report["BASIC_EPS"],
    }


def summarize_all_stock_fundamentals() -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []
    stock_fundamental_summaries = []

    project_root_path = Path(__file__).resolve().parent.parent

    stock_data_dir_path = project_root_path / "data"

    try:
        stock_code_list: list[str] = read_stock_code_list(stock_data_dir_path)

    except Exception as error:
        print(f"Failed to read stock code list: {error}")
        return

    stock_fundamentals_dir_path = stock_data_dir_path / "fundamentals"

    stock_fundamentals_dir_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    for stock_code in stock_code_list:
        print(f"Start fetching fundamental data " f"for {stock_code}...")

        try:
            stock_fundamental_summary = fetch_stock_fundamental_summary(stock_code)

            stock_fundamental_summaries.append(stock_fundamental_summary)

            print(f"Finished fetching fundamental data " f"for {stock_code}")

            success_count += 1

        except Exception as error:
            print(f"Failed to fetch fundamental data " f"for {stock_code}: {error}")

            failed_count += 1
            failed_codes.append(stock_code)

    stock_fundamental_summary_data = pd.DataFrame(stock_fundamental_summaries)

    stock_fundamental_summary_path = (
        stock_fundamentals_dir_path / "stock_fundamental_summary.csv"
    )

    stock_fundamental_summary_data.to_csv(
        stock_fundamental_summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    if failed_count == 0:
        print("\nSuccessfully fetched fundamental data " "for all stock datasets.\n")

    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")

    print(f"Summary file saved to: " f"{stock_fundamental_summary_path}")


if __name__ == "__main__":
    summarize_all_stock_fundamentals()
