from pathlib import Path
from data_utils import read_stock_code_list
import akshare as ak
import pandas as pd


def fetch_stock_valuation(
    stock_code_list: list[str],
) -> pd.DataFrame:
    all_stock_valuation = ak.stock_zh_a_spot_em()

    if all_stock_valuation.empty:
        raise ValueError("No stock valuation data returned.")

    pure_stock_code_list = [stock_code[-6:] for stock_code in stock_code_list]

    selected_columns = [
        "代码",
        "名称",
        "最新价",
        "市盈率-动态",
        "市净率",
        "总市值",
        "流通市值",
    ]

    stock_valuation = all_stock_valuation.loc[
        all_stock_valuation["代码"].isin(pure_stock_code_list),
        selected_columns,
    ].copy()

    if stock_valuation.empty:
        raise ValueError("No valuation data matched the sample stock codes.")

    return stock_valuation


def fetch_all_stock_valuation() -> None:
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

    try:
        print("Start fetching valuation data " "for all sample stocks...")

        stock_valuation = fetch_stock_valuation(stock_code_list)

        stock_valuation_path = (
            stock_fundamentals_dir_path / "stock_valuation_summary.csv"
        )

        stock_valuation.to_csv(
            stock_valuation_path,
            index=False,
            encoding="utf-8-sig",
        )

        print("\nSuccessfully fetched valuation data " "for all sample stocks.\n")

        print(f"Summary file saved to: " f"{stock_valuation_path}")

    except Exception as error:
        print(f"Failed to fetch stock valuation data: " f"{error}")


if __name__ == "__main__":
    fetch_all_stock_valuation()
