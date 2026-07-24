from pathlib import Path

import pandas as pd


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


def inspect_all_stock_data() -> None:
    project_root_path = Path(__file__).resolve().parent.parent
    try:
        stock_list_path = project_root_path / "data" / "stock_code_list.csv"
        stock_list_df = pd.read_csv(stock_list_path, header=None, names=["stock_code"])
        stock_list = (
            stock_list_df["stock_code"].dropna().astype(str).str.strip().tolist()
        )
    except FileNotFoundError:
        print("No such file: 'stock_code.csv'.")
        return

    stock_data_dir_path = project_root_path / "data"
    inspection_result_dir_path = (
        stock_data_dir_path / "data_unadjusted_inspection_results"
    )
    inspection_result_dir_path.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_count = 0
    failed_to_read_stock = []

    for stock_code in stock_list:
        print(f"start inspecting {stock_code} ...")
        file_path = (
            stock_data_dir_path
            / "raw_unadjusted"
            / f"{stock_code}_daily_unadjusted_tx.csv"
        )

        try:
            stock_inspection_result = inspect_single_stock_data(stock_code, file_path)

            inspection_result_path = inspection_result_dir_path / f"{stock_code}.txt"

            with open(inspection_result_path, "w", encoding="utf-8") as f:
                f.write(stock_inspection_result)

            success_count += 1

        except Exception as error:
            print(f"Failed to inspect {stock_code} : {error}")
            failed_to_read_stock.append(stock_code)
            failed_count += 1

        print(f"Finished inspecting {stock_code}.")

    if failed_count == 0:
        print("All stock data inspected.")
        print(f"Successfully inspected: {success_count}")
        print(f"Failed inspected: {failed_count}")
    else:
        print(f"Successfully inspected: {success_count}")
        print(f"Failed inspected: {failed_count}")
        print(failed_to_read_stock=[])


if __name__ == "__main__":
    inspect_all_stock_data()
