from pathlib import Path
from helper_functions import *
import pandas as pd
import numpy as np

def summarize_stock_activity(
    stock_data: pd.DataFrame,
    stock_code: str,
) -> dict:
    
    valid_volume_ratio = stock_data["volume_ratio"].dropna()
    valid_volatility = stock_data["rolling_volatility_20"].dropna()

    volume_spike_days = (stock_data["volume_ratio"] >= 1.5).sum()
    large_rise_days = (stock_data["daily_return"] >= 0.05).sum()
    large_fall_days = (stock_data["daily_return"] <= -0.05).sum()
    high_amplitude_days = (stock_data["amplitude"] >= 0.08).sum()

    trading_days = len(stock_data)

    return {
        "stock_code": stock_code,
        "trading_days": trading_days,
        "average_daily_return": stock_data["daily_return"].mean(),
        "average_amplitude": stock_data["amplitude"].mean(),
        "average_amount": stock_data["amount"].mean(),
        "average_volume_ratio": valid_volume_ratio.mean(),
        "average_volatility_20": valid_volatility.mean(),
        "volume_spike_days": volume_spike_days,
        "large_rise_days": large_rise_days,
        "large_fall_days": large_fall_days,
        "high_amplitude_days": high_amplitude_days,
        "volume_spike_ratio": volume_spike_days / trading_days,
        "large_move_ratio": (
            large_rise_days + large_fall_days
        ) / trading_days,
    }


def summarize_all_stock_activity() -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []
    project_root_path = Path(__file__).resolve().parent.parent
    stock_data_dir_path = project_root_path / "data"

    try:
        stock_code_list: list[str] = read_stock_code_list(stock_data_dir_path)
    except RuntimeError as error:
        print(f"failed to read stock data list : {error}")
        return

    stock_activity_summary_list: list[dict] = []
    for stock_code in stock_code_list:
        print(f"Start summarizing {stock_code}...")

        try:
            stock_activity_path = stock_data_dir_path / "activity" / f"{stock_code}_with_activity_columns.csv"
            stock_activity = load_stock_data_from_csv(stock_activity_path, stock_code)
            stock_activity_summary = summarize_stock_activity(stock_activity, stock_code)
            stock_activity_summary_list.append(stock_activity_summary)
            success_count += 1
            print(f"Finished summarized the activity for {stock_code}")
        except Exception as error:
            print(f"failed to summarize {stock_code} : {error}")
            failed_count += 1
            failed_codes.append(stock_code)
            stock_activity_summary_list.append(
                {
                    "stock_code": stock_code,
                    "trading_days": np.nan,
                    "average_daily_return": np.nan,
                    "average_amplitude": np.nan,
                    "average_amount": np.nan,
                    "average_volume_ratio": np.nan,
                    "average_volatility_20": np.nan,
                    "volume_spike_days": np.nan,
                    "large_rise_days": np.nan,
                    "large_fall_days": np.nan,
                    "high_amplitude_days": np.nan,
                    "volume_spike_ratio": np.nan,
                    "large_move_ratio": np.nan,
                }
            )

    stock_activity_summary_list_df = pd.DataFrame(stock_activity_summary_list)
    stock_activity_summary_path = stock_data_dir_path / "analysis" / "stock_activity_summary.csv"

    stock_activity_summary_list_df.to_csv(stock_activity_summary_path, encoding='utf-8')

    if failed_count == 0:
        print("\nSuccessfully summarized the activity for all stocks.\n")
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")

    print(stock_activity_summary_list_df.head())
    print(stock_code_list)

if __name__ == "__main__":
    summarize_all_stock_activity()





