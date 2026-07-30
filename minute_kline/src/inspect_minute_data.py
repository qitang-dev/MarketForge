from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
STOCK_MINUTE_DATA_DIR = STOCK_DATA_DIR / "minute"
STOCK_MINUTE_RAW_DATA_DIR = STOCK_MINUTE_DATA_DIR / "raw"

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


def inspect_all_stock_minute_data(adjust_flag: str) -> None:
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
