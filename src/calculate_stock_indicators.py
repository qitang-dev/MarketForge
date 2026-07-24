from pathlib import Path
from helper_functions import *
import pandas as pd


def calculate_moving_average(
        stock_data: pd.DataFrame, 
        windows: list[int], 
        value_column="close",
        ) -> pd.DataFrame:

    if stock_data.empty:
        raise ValueError("Stock data cannot be empty.")

    result = stock_data.copy()

    for win in windows:
        if win <= 0:
            raise ValueError("The window size must be greater than 0.")
        ma_column: pd.Series = result[value_column].rolling(window=win).mean().round(2)
        result[f"ma_{win}"] = ma_column

    return result


def calculate_all_moving_average(windows=[3, 5, 7, 10, 20, 21]) -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []
    project_root = Path(__file__).resolve().parent.parent
    stock_data_dir_path = project_root / "data"
    stock_code_list_path = stock_data_dir_path / "stock_code_list.csv"

    try:
        stock_code_df = pd.read_csv(
            stock_code_list_path,
            header=None,
            names=["stock_code"],
        )
    except FileNotFoundError as error:
        print(f"No such file 'stock_code_list.csv' in {stock_code_list_path} : {error}")
        return 

    stock_code_list = stock_code_df["stock_code"].tolist()
    stock_data_indicators_path: Path = stock_data_dir_path / "indicators"
    stock_data_indicators_path.mkdir(parents=True, exist_ok=True)

    for stock_code in stock_code_list:
        print(f"Start calculating moving average columns for {stock_code}...")
        stock_data_path = stock_data_dir_path / "cleaned" / f"cleaned_{stock_code}_daily_qfq_tx.csv"
        try:
            stock_data = load_stock_data_from_csv(stock_data_path, stock_code)
            stock_data_with_ma = calculate_moving_average(stock_data, windows)
            stock_data_with_ma_path = stock_data_indicators_path / f"cleaned_{stock_code}_with_ma_columns.csv"
            stock_data_with_ma.to_csv(stock_data_with_ma_path, encoding='utf-8')
            print(f"Finished calculating moving average columns for {stock_code}")
            success_count += 1

        except RuntimeError as error_0:
            print(f"Failed to calculate moving average columns for {stock_code} : {error_0}")
            failed_count += 1
            failed_codes.append(stock_code)

        except ValueError as error_1:
            print(f"Failed to calculate moving average columns for {stock_code} : {error_1}")
            failed_count += 1
            failed_codes.append(stock_code)

    if failed_count == 0:
        print("\nSuccessfully calculated moving average columns for all stock data.\n")
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")

if __name__ == "__main__":
    calculate_all_moving_average()



