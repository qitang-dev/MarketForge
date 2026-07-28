from pathlib import Path
from data_utils import *
import baostock as bs
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
STOCK_MINUTE_DATA_DIR = STOCK_DATA_DIR / "minute"
STOCK_MINUTE_RAW_DATA_DIR = STOCK_MINUTE_DATA_DIR / "raw"

ADJUST_NAME_MAP = {
    "1": "hfq",
    "2": "qfq",
    "3": "unadjusted",
}


def fetch_baostock_minute_data(
    stock_code: str,
    start_date: str,
    end_date: str,
    period: str,
    adjust_flag: str,
) -> pd.DataFrame:

    try:
        query_result = bs.query_history_k_data_plus(
            code=stock_code,
            fields=("date,time,code,open,high,low,close," "volume,amount,adjustflag"),
            start_date=start_date,
            end_date=end_date,
            frequency=period,
            adjustflag=adjust_flag,
        )

        if query_result.error_code != "0":
            raise RuntimeError(
                f"Failed to fetch {stock_code}: " f"{query_result.error_msg}."
            )

        data_rows = []

        while query_result.next():
            data_rows.append(query_result.get_row_data())

        stock_data = pd.DataFrame(
            data_rows,
            columns=query_result.fields,
        )

    except Exception as error:
        raise RuntimeError(f"[FAILED] : {error}") from error

    if stock_data.empty:
        raise ValueError(f"Empty minute data returned " f"for {stock_code}.")

    return stock_data


def fetch_all_stock_minute_data(adjust_flag: str) -> None:
    fetch_result = []
    success_count = 0
    failed_count = 0

    if adjust_flag not in ADJUST_NAME_MAP:
        raise ValueError("The adjust_flag must be '1', '2', or '3'.")

    try:
        stock_code_list: list[str] = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read stock code list: {error}")
        return

    STOCK_MINUTE_RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    stock_minute_raw_data_adjust_flag_dir_path = (
        STOCK_MINUTE_RAW_DATA_DIR / f"{ADJUST_NAME_MAP[adjust_flag]}"
    )
    stock_minute_raw_data_adjust_flag_dir_path.mkdir(parents=True, exist_ok=True)

    login_result = bs.login()

    if login_result.error_code != "0":
        raise RuntimeError(
            f"Failed to log in to BaoStock: " f"{login_result.error_msg}."
        )

    try:
        for stock_code in stock_code_list:
            print(f"Start processing {stock_code}...")

            baostock_code = convert_to_baostock_code(stock_code)

            try:
                stock_minute_data = fetch_baostock_minute_data(
                    stock_code=baostock_code,
                    start_date="2024-07-28",
                    end_date="2026-07-28",
                    period="5",
                    adjust_flag=adjust_flag,
                )

                adjust_name = ADJUST_NAME_MAP[adjust_flag]

                output_file_path = (
                    stock_minute_raw_data_adjust_flag_dir_path
                    / f"{stock_code}_5min_{adjust_name}_baostock.csv"
                )

                stock_minute_data.to_csv(
                    output_file_path,
                    index=False,
                    encoding="utf-8-sig",
                )

                fetch_result.append(
                    {
                        "stock_code: ": stock_code,
                        "status: ": "success",
                        "rows: ": len(stock_minute_data),
                        "columns: ": len(stock_minute_data.columns),
                        "error: ": None,
                    }
                )
                success_count += 1
                print(f"Finished processing {stock_code}.")

            except Exception as error:
                fetch_result.append(
                    {
                        "stock_code: ": stock_code,
                        "status: ": "failed",
                        "rows: ": 0,
                        "columns: ": 0,
                        "error: ": str(error),
                    }
                )
                failed_count += 1
                print(
                    f"[Failed] unable to fetch the minute data for {stock_code} : {error}"
                )
    finally:
        bs.logout()

    if failed_count == 0:
        print("All stock minute data fetched successfull!")
    else:
        print(f"Successful: {success_count}")
        print(f"Failed: {failed_count}")

    print(pd.DataFrame(fetch_result))


if __name__ == "__main__":
    fetch_all_stock_minute_data("3")
    fetch_all_stock_minute_data("2")
