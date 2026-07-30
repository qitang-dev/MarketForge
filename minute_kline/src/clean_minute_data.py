from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
STOCK_MINUTE_DATA_DIR = STOCK_DATA_DIR / "minute"
STOCK_MINUTE_RAW_DATA_DIR = STOCK_MINUTE_DATA_DIR / "raw"

ADJUST_FLAG_MAP = {
    "1": "hfq",
    "2": "qfq",
    "3": "unadjusted",
}


def clean_stock_minute_data(
    stock_data: pd.DataFrame,
    datetime_as_index=True,
) -> pd.DataFrame:
    cleaned_data = stock_data.copy()

    cleaned_data.columns = cleaned_data.columns.str.strip()

    cleaned_data["datetime"] = pd.to_datetime(
        cleaned_data["time"].astype(str).str[:14],
        format="%Y%m%d%H%M%S",
        errors="coerce",
    )

    numeric_columns = ["open", "high", "low", "close", "volume", "amount"]

    for column in numeric_columns:
        cleaned_data[column] = pd.to_numeric(
            cleaned_data[column],
            errors="coerce",
        )

    required_columns = ["datetime", *numeric_columns]
    cleaned_data = cleaned_data[required_columns]

    cleaned_data = cleaned_data.dropna(subset=required_columns)
    cleaned_data = cleaned_data.drop_duplicates(subset=["datetime"], keep="last")

    cleaned_data = cleaned_data.sort_values("datetime", ascending=True).reset_index(
        drop=True
    )

    valid_price_mask = (
        (cleaned_data["high"] >= cleaned_data["open"])
        & (cleaned_data["high"] >= cleaned_data["close"])
        & (cleaned_data["high"] >= cleaned_data["low"])
        & (cleaned_data["low"] <= cleaned_data["open"])
        & (cleaned_data["low"] <= cleaned_data["close"])
    )

    cleaned_data = cleaned_data.loc[valid_price_mask].reset_index(drop=True)

    if datetime_as_index:
        cleaned_data = cleaned_data.set_index("datetime")

    return cleaned_data


def clean_all_stock_minute_data(adjust_flag: str) -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []

    try:
        cleaned_data_dir_path = STOCK_MINUTE_DATA_DIR / "cleaned"
        cleaned_data_dir_path.mkdir(parents=True, exist_ok=True)

        cleaned_data_adjust_dir_path = (
            cleaned_data_dir_path / f"{ADJUST_FLAG_MAP[adjust_flag]}"
        )
        cleaned_data_adjust_dir_path.mkdir(parents=True, exist_ok=True)

    except Exception as error:
        print(f"[FAILED] unable to create directory : {error}")
        return

    try:
        stock_code_list: list[str] = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read the stock code list : {error}")
        return

    for stock_code in stock_code_list:

        try:
            print(f"Start cleaning {stock_code}...")
            input_raw_data_path = (
                STOCK_MINUTE_RAW_DATA_DIR
                / f"{ADJUST_FLAG_MAP[adjust_flag]}"
                / f"{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_baostock.csv"
            )
            output_cleaned_data_path = (
                cleaned_data_adjust_dir_path
                / f"cleaned_{stock_code}_5min_{ADJUST_FLAG_MAP[adjust_flag]}_baostock.csv"
            )

            raw_stock_data = pd.read_csv(input_raw_data_path, encoding="utf-8")
            cleaned_stock_data = clean_stock_minute_data(raw_stock_data)

            cleaned_stock_data.to_csv(
                output_cleaned_data_path,
                index=True,
                index_label="datetime",
                encoding="utf-8",
            )

            success_count += 1
            print(f"Finished cleaning {stock_code}...")

        except Exception as error:
            failed_count += 1
            failed_codes.append(stock_code)
            print(f"[FAILED] unable to clean the stock data for {stock_code} : {error}")

    if failed_count == 0:
        print("\nSuccessfully cleaned all raw stock minute data!\n")
    else:
        print(f"Failed to clean raw stock minute data for {failed_count} stocks.")
        print(f"Failed Code(s): {failed_codes}")
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")


if __name__ == "__main__":
    clean_all_stock_minute_data("2")
    clean_all_stock_minute_data("3")
