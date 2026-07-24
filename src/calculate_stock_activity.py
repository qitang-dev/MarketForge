from pathlib import Path
from data_utils import *
import pandas as pd


def calculate_stock_data_activity(stock_data: pd.DataFrame) -> pd.DataFrame:
    if stock_data.empty:
        raise ValueError("The stock data cannot be empty.")

    result = stock_data.copy()

    result["daily_return"] = result["close"].pct_change().round(2)

    result["amplitude"] = (
        (result["high"] - result["low"]) / result["close"].shift(1)
    ).round(2)

    result["amount_change"] = result["amount"].pct_change().round(2)

    result["amount_ma_20"] = result["amount"].rolling(window=20).mean().round(2)

    result["volume_ratio"] = (result["amount"] / result["amount_ma_20"]).round(2)

    result["rolling_volatility_20"] = (
        result["daily_return"].rolling(window=20).std(ddof=1).round(2)
    )

    return result


def calculate_all_stock_data_activity() -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []
    project_root_path = Path(__file__).resolve().parent.parent
    stock_data_dir_path = project_root_path / "data"

    try:
        stock_code_list: list[str] = read_stock_code_list(stock_data_dir_path)
    except Exception as error:
        print(f"failed to read stock code list : {error}")
        return

    stock_data_activity_dir_path = stock_data_dir_path / "activity"
    stock_data_activity_dir_path.mkdir(parents=True, exist_ok=True)

    for stock_code in stock_code_list:
        print(f"Start calculating the activity for {stock_code}...")
        stock_data_indicators_path = (
            stock_data_dir_path
            / "indicators"
            / f"cleaned_{stock_code}_with_ma_columns.csv"
        )

        try:
            stock_data_indicators = load_stock_data_from_csv(
                stock_data_indicators_path, stock_code
            )
            stock_data_activity = calculate_stock_data_activity(stock_data_indicators)

            stock_data_activity_path = (
                stock_data_activity_dir_path / f"{stock_code}_with_activity_columns.csv"
            )
            stock_data_activity.to_csv(stock_data_activity_path, encoding="utf-8")

            print(f"Finished calculating the activity for {stock_code}")
            success_count += 1

        except Exception as error:
            print(f"Failed to calculate the activity of {stock_code} : {error}")
            failed_count += 1
            failed_codes.append(stock_code)

    if failed_count == 0:
        print("\nSuccessfully calculated the activity for all stock data.\n")
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")


if __name__ == "__main__":
    calculate_all_stock_data_activity()
