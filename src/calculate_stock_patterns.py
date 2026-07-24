from pathlib import Path
from helper_functions import *
import pandas as pd


def calculate_stock_data_patterns(stock_data: pd.DataFrame) -> pd.DataFrame:
    result = stock_data.copy()

    result["rolling_high_20"] = (
    result["high"]
    .rolling(window=20)
    .max().round(2)
    )

    result["rolling_low_20"] = (
        result["low"]
        .rolling(window=20)
        .min().round(2)
    )

    result["rolling_mean_close_20"] = (
        result["close"]
        .rolling(window=20)
        .mean().round(2)
    )

    result["box_width_20"] = ((
        result["rolling_high_20"] - result["rolling_low_20"]
    ) / result["rolling_mean_close_20"]).round(2)

    result["ma_20_slope"] = (
        (result["ma_20"] / result["ma_20"].shift(5) - 1).round(2)
    )

    result["sideways_box"] = (
        (result["box_width_20"] <= 0.12)
        & (result["ma_20_slope"].abs() <= 0.03)
    )

    result["violent_fluctuation"] = (
        (result["amplitude"] >= 0.08)
        | (result["daily_return"].abs() >= 0.05)
    )

    result["volume_price_surge"] = (
        (result["volume_ratio"] >= 1.5)
        & (result["daily_return"] >= 0.03)
    )

    return result


def calculate_all_stock_data_patterns() -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []

    project_root_path = Path(__file__).resolve().parent.parent
    stock_data_dir_path = project_root_path / "data"

    try:
        stock_code_list: list[str] = read_stock_code_list(stock_data_dir_path)

    except Exception as error:
        print(f"Failed to read stock code list: {error}")
        return

    stock_data_patterns_dir_path = stock_data_dir_path / "patterns"

    stock_data_patterns_dir_path.mkdir(parents=True, exist_ok=True)

    for stock_code in stock_code_list:
        print(
            f"Start calculating pattern indicators for {stock_code}..."
        )

        stock_data_activity_path = stock_data_dir_path / "activity"/ f"{stock_code}_with_activity_columns.csv"

        try:
            stock_data_activity = load_stock_data_from_csv(
                stock_data_activity_path,
                stock_code,
            )

            stock_data_patterns = (
                calculate_stock_data_patterns(
                    stock_data_activity
                )
            )

            stock_data_patterns_path = (
                stock_data_patterns_dir_path
                / f"{stock_code}_with_pattern_columns.csv"
            )

            stock_data_patterns.to_csv(
                stock_data_patterns_path,
                encoding="utf-8",
            )

            print(
                f"Finished calculating pattern indicators "
                f"for {stock_code}"
            )

            success_count += 1

        except Exception as error:
            print(
                f"Failed to calculate pattern indicators "
                f"for {stock_code}: {error}"
            )

            failed_count += 1
            failed_codes.append(stock_code)

    if failed_count == 0:
        print(
            "\nSuccessfully calculated pattern indicators "
            "for all stock data.\n"
        )
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")


if __name__ == "__main__":
    calculate_all_stock_data_patterns()