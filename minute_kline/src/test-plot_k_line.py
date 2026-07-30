from pathlib import Path
from data_utils import read_stock_code_list

import pandas as pd
import mplfinance as mpf

import matplotlib.pyplot as plt

plt.rcParams["font.weight"] = "normal"
plt.rcParams["axes.titleweight"] = "normal"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
STOCK_MINUTE_DATA_DIR = STOCK_DATA_DIR / "minute"
STOCK_MINUTE_CLEANED_DATA_DIR = STOCK_MINUTE_DATA_DIR / "cleaned"

ADJUST_FLAG_MAP = {
    "1": "hfq",
    "2": "qfq",
    "3": "unadjusted",
}


def plot_stock_kline(
    stock_data: pd.DataFrame,
    stock_code: str,
    adjust_flag: str,
    output_file_path: Path,
    data_size=200,
) -> None:

    plot_data = stock_data.tail(data_size)

    mpf.plot(
        plot_data,
        type="candle",
        volume=True,
        mav=(5, 10, 20),
        title=f"{stock_code} 5-Minute {ADJUST_FLAG_MAP[adjust_flag].upper()} Candlestick Chart",
        ylabel="Price",
        ylabel_lower="Volume",
        figratio=(16, 9),
        figscale=1.2,
        style="yahoo",
        show_nontrading=False,
        savefig=output_file_path,
    )


def plot_all_stock_kline(adjust_flag: str) -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []

    try:
        output_dir_path = (
            PROJECT_ROOT / "figure" / "k_line" / f"{ADJUST_FLAG_MAP[adjust_flag]}"
        )
        output_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"[FAILED unable to create the related folder : {error}")
        return

    try:
        stock_code_list = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read the stock code list : {error}")
        return

    for stock_code in stock_code_list:
        print(f"Start ploting the k_line for {stock_code}...")
        try:
            stock_file_path = (
                STOCK_MINUTE_CLEANED_DATA_DIR
                / f"{ADJUST_FLAG_MAP[adjust_flag]}"
                / f"cleaned_{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_baostock.csv"
            )

            stock_data = pd.read_csv(
                stock_file_path, index_col="datetime", parse_dates=["datetime"]
            )

            output_file_path = (
                output_dir_path
                / f"{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_kline.png"
            )

            plot_stock_kline(
                stock_data,
                stock_code,
                adjust_flag,
                output_file_path,
                100,
            )
            success_count += 1
            print(f"Finished ploting the k_line for {stock_code}...")

        except Exception as error:
            print(f"[FAILED] unable to plot the k_line for {stock_code} : {error}")

    if failed_count == 0:
        print("\nSuccessfully ploting the k_line for all stocks!\n")
    else:
        print(f"Failed to plot the k_line for {failed_count} stocks.")
        print(f"Failed Code(s): {failed_codes}")
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")


if __name__ == "__main__":
    plot_all_stock_kline("2")
    plot_all_stock_kline("3")
