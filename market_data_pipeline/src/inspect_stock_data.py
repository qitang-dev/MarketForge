from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCK_DATA_DIR = STOCK_DATA_DIR / "raw"


def inspect_single_stock_data(stock_code: str, stock_data_path: Path) -> str:
    try:
        stock_data = pd.read_csv(stock_data_path)
    except Exception as error:
        raise RuntimeError(f"Failed to read {stock_code} : {error}") from error

    unnamed_cols = [
        column for column in stock_data.columns if str(column).startswith("Unnamed")
    ]

    empty_cols = stock_data.columns[stock_data.isna().all(axis=0)].tolist()

    contents = f"{stock_code} Inspection Result\n"
    contents += f"\nFile Path: {stock_data_path}\n"
    contents += f"\n(Rows, Cols): {stock_data.shape}\n"
    contents += f"\nColumns: {stock_data.columns.to_list()}\n"
    contents += f"\nData Type in Cols: \n{stock_data.dtypes}\n"
    contents += f"\nEmpty Column(s): {empty_cols}\n"
    contents += f"\nUnnamed Column(s): {unnamed_cols}\n"

    return contents


def inspect_all_stock_data(adjust_flag: str) -> None:

    try:
        stock_code_list: list[str] = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read the stock code list : {error}")
        return

    try:
        output_dir_path = RAW_STOCK_DATA_DIR / f"{adjust_flag}" / "inspection_result"
        output_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"[FAILED] unable to created the directory : {error}")
        return

    success_count = 0
    failed_count = 0
    failed_codes = []

    for stock_code in stock_code_list:
        print(f"start inspecting {stock_code} ...")
        input_file_path = (
            RAW_STOCK_DATA_DIR
            / f"{adjust_flag}"
            / f"{stock_code}_daily_{adjust_flag}_tx.csv"
        )

        try:
            stock_inspection_result = inspect_single_stock_data(
                stock_code, input_file_path
            )

            inspection_result_path = output_dir_path / f"{stock_code}.txt"

            with open(inspection_result_path, "w", encoding="utf-8") as f:
                f.write(stock_inspection_result)

            success_count += 1

        except Exception as error:
            print(f"Failed to inspect {stock_code} : {error}")
            failed_codes.append(stock_code)
            failed_count += 1

        print(f"Finished inspecting {stock_code}.")

    if failed_count == 0:
        print("All stock data inspected.")
        print(f"Successfully inspected: {success_count}")
        print(f"Failed inspected: {failed_count}\n")
    else:
        print(f"Successfully inspected: {success_count}")
        print(f"Failed inspected: {failed_count}")
        print(f"Failed to inspect stock code(s): {failed_codes}\n")


if __name__ == "__main__":
    inspect_all_stock_data("qfq")
    inspect_all_stock_data("unadjusted")
