from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
STOCK_MINUTE_DATA_DIR = STOCK_DATA_DIR / "minute"
STOCK_MINUTE_RAW_DATA_DIR = STOCK_MINUTE_DATA_DIR / "raw"
STOCK_MINUTE_CLEANED_DATA_DIR = STOCK_MINUTE_DATA_DIR / "cleaned"

ADJUST_FLAG_MAP = {
    "1": "hfq",
    "2": "qfq",
    "3": "unadjusted",
}


def inspect_stock_minute_data(stock_data_path: Path, stock_code: str) -> None:
    try:
        stock_data = pd.read_csv(stock_data_path, encoding="utf-8")
    except Exception as error:
        raise RuntimeError(f"[FAILED] unable to read {stock_code} : {error}") from error

    unnamed_columns = [
        column for column in stock_data.columns if str(column).startswith("Unnamed")
    ]

    empty_columns = stock_data.columns[stock_data.isna().all(axis=0)].tolist()

    contents = f"{stock_code} Inspection Result\n"
    contents += f"\nFile Path: {stock_data_path}\n"
    contents += f"\nRows: {len(stock_data)}\n"
    contents += f"\nColumns: {len(stock_data.columns)}\n"
    contents += f"\nColumns: {stock_data.columns.to_list()}\n"
    contents += f"\nData Type in Cols: \n{stock_data.dtypes}\n"
    contents += f"\nEmpty Column(s): {empty_columns}\n"
    contents += f"\nUnnamed Column(s): {unnamed_columns}\n"

    return contents


from pathlib import Path

import pandas as pd


def inspect_the_missing_value_for_cleaned_minute_data(
    file_path: Path,
) -> str:
    stock_data = pd.read_csv(
        file_path,
        parse_dates=["datetime"],
    )

    stock_data = (
        stock_data.dropna(subset=["datetime"])
        .sort_values("datetime")
        .drop_duplicates(
            subset=["datetime"],
            keep="last",
        )
    )

    daily_bar_counts = stock_data.groupby(stock_data["datetime"].dt.date).size()

    incomplete_days = daily_bar_counts[daily_bar_counts != 48]

    contents = ""

    contents += f"File: {file_path.name}\n"

    contents += f"Total rows: {len(stock_data)}\n"
    contents += f"Duplicated datetime: {stock_data['datetime'].duplicated().sum()}\n"

    contents += f"Missing OHLCV values: {stock_data[['open', 'high', 'low', 'close', 'volume']].isna().sum().sum()}\n"

    contents += f"Trading days with data: {len(daily_bar_counts)}"

    if incomplete_days.empty:
        contents += "[PASSED] Every recorded trading day contains 48 bars."
    else:
        contents += f"[NOTICE] Days with fewer or more than 48 bars: {incomplete_days}"

    return contents


def inspect_all_stock_minute_data(
    adjust_flag: str, missing_value_inspection=True
) -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []

    try:

        stock_code_list = read_stock_code_list(STOCK_DATA_DIR)

        input_stock_minute_data_dir_path = (
            STOCK_MINUTE_RAW_DATA_DIR / f"{ADJUST_FLAG_MAP[adjust_flag]}"
        )

        output_inspection_results_dir_path = (
            input_stock_minute_data_dir_path / "data_inspection_results"
        )

        output_inspection_results_dir_path.mkdir(parents=True, exist_ok=True)

    except RuntimeError as error_0:
        print(f"[FAILED] unable to read stock code list: {error_0}")
        return
    except Exception as error_1:
        print(f"[UNEXCEPTED ERROR] : {error_1}")
        return

    if missing_value_inspection:
        try:
            input_cleaned_data_dir_path = (
                STOCK_MINUTE_CLEANED_DATA_DIR / f"{ADJUST_FLAG_MAP[adjust_flag]}"
            )
            missing_value_inspection_result_dir_path = (
                input_cleaned_data_dir_path / "missing_value_inspection_result"
            )
            missing_value_inspection_result_dir_path.mkdir(parents=True, exist_ok=True)

        except Exception as error:
            print(f"[UNEXCEPTED ERROR] : {error}")
            return

    for stock_code in stock_code_list:
        print(f"Start inspecting {stock_code}...")
        try:

            stock_data_path = (
                input_stock_minute_data_dir_path
                / f"{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_baostock.csv"
            )

            inspection_result = inspect_stock_minute_data(stock_data_path, stock_code)

            output_inspection_result_path = (
                output_inspection_results_dir_path
                / f"{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_inspection_result.txt"
            )

            with open(output_inspection_result_path, "w") as f:
                f.write(inspection_result)

            if missing_value_inspection:

                input_clean_stock_data_file_path = (
                    input_cleaned_data_dir_path
                    / f"cleaned_{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_baostock.csv"
                )
                output_missing_value_inspection_result_file_path = (
                    missing_value_inspection_result_dir_path
                    / f"{stock_code}_missing_value_inspection_result.txt"
                )

                missing_value_inspection_result: str = (
                    inspect_the_missing_value_for_cleaned_minute_data(
                        input_clean_stock_data_file_path
                    )
                )
                with open(output_missing_value_inspection_result_file_path, "w") as f:
                    f.write(missing_value_inspection_result)

            success_count += 1
            print(f"Finished inspecting {stock_code}.")

        except Exception as error:
            print(f"[FAILED] unable to inspect {stock_code} : {error}")
            failed_count += 1
            failed_codes.append(stock_code)

    if failed_count == 0:
        print("\nSuccessfully inspected all stock minute data.\n")
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")


if __name__ == "__main__":
    inspect_all_stock_minute_data("2")
    inspect_all_stock_minute_data("3")
