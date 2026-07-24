from pathlib import Path

import pandas as pd
import akshare as ak


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


def store_stock_data(stock_data: pd.DataFrame, stock_code: str, adjust: str) -> None:

    project_root_path = Path(__file__).resolve().parent.parent
    output_dir_path = project_root_path / "data" / "raw_unadjusted"

    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_path = output_dir_path / f"{stock_code}_daily_{adjust}_tx.csv"

    stock_data.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Stored {stock_code} at {output_path}.")


def fetch_all_stock_data() -> None:
    fetch_results = []
    project_root_path = Path(__file__).resolve().parent.parent

    try:
        target_file_path = project_root_path / "data" / "stock_code_list.csv"
        stock_code_df = pd.read_csv(target_file_path, header=None, names=["stock_code"])
    except FileNotFoundError:
        print("No such 'stock_code_list.csv' existed.")
        return

    stock_code_list = (
        stock_code_df["stock_code"].dropna().astype(str).str.strip().tolist()
    )
    for stock_code in stock_code_list:
        print(f"Processing: {stock_code}")
        try:
            stock_data = fetch_stock_data(stock_code, "20250101", "20251231", "")
            store_stock_data(stock_data, stock_code, "unadjusted")

            fetch_results.append(
                {
                    "stock_code": stock_code,
                    "status": "success",
                    "rows": len(stock_data),
                    "Error": None,
                }
            )
        except Exception as error:
            fetch_results.append(
                {
                    "stock_code": stock_code,
                    "status": "failed",
                    "rows": 0,
                    "Error": str(error),
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
    print(f"Failed: {failed_count}")


if __name__ == "__main__":
    fetch_all_stock_data()
