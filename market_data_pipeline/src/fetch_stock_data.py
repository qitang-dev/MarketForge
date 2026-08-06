from pathlib import Path
from data_utils import read_stock_code_list

import pandas as pd
import akshare as ak

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCK_DATA_DIR = STOCK_DATA_DIR / "raw"

ADJUST_FLAG_MAP = {
    "unadjusted": "",
    "qfq": "qfq",
    "hfq": "hfq",
}


def fetch_stock_data(
    stock_code: str, start_date: str, end_date: str, adjust: str
) -> pd.DataFrame:

    try:
        stock_data: pd.DataFrame = ak.stock_zh_a_hist_tx(
            symbol=stock_code,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )
    except Exception as error:
        raise RuntimeError(f"Failed to fetch {stock_code} : {error}.") from error

    if stock_data.empty:
        raise ValueError(f"Empty stock data returned from {stock_code}.")

    return stock_data


def fetch_all_stock_data(adjust_flag: str) -> None:
    fetch_results = []

    try:
        stock_code_list: list[str] = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read the stock code list : {error}")
        return

    try:
        output_dir_path = RAW_STOCK_DATA_DIR / f"{adjust_flag}"
        output_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"[FAILED] unable to created the directory : {error}")
        return

    for stock_code in stock_code_list:
        print(f"Start fetching {stock_code}...")
        try:
            stock_data = fetch_stock_data(
                stock_code, "20250101", "20251231", ADJUST_FLAG_MAP[adjust_flag]
            )

            output_file_path = (
                output_dir_path / f"{stock_code}_daily_{adjust_flag}_tx.csv"
            )

            stock_data.to_csv(output_file_path, index=False, encoding="utf-8-sig")

            print(f"Finished fetching {stock_code}...")

            fetch_results.append(
                {
                    "stock_code": stock_code,
                    "status": "success",
                    "rows": len(stock_data),
                    "error": None,
                }
            )
        except Exception as error:
            fetch_results.append(
                {
                    "stock_code": stock_code,
                    "status": "failed",
                    "rows": 0,
                    "error": str(error),
                }
            )

    fetch_results_df = pd.DataFrame(
        fetch_results, columns=["stock_code", "status", "rows", "error"]
    )
    result_status = fetch_results_df["status"].value_counts()
    success_count = result_status.get("success", 0)
    failed_count = result_status.get("failed", 0)

    print(fetch_results_df)
    print(f"Successful:  {success_count}")
    print(f"Failed: {failed_count}\n")


if __name__ == "__main__":
    fetch_all_stock_data("qfq")
    fetch_all_stock_data("unadjusted")
