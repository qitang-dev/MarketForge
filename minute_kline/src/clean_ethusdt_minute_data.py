from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = PROJECT_ROOT / "data" / "crypto" / "raw" / "ETHUSDT_5min_binance_us.csv"

CLEANED_DATA_DIRECTORY = PROJECT_ROOT / "data" / "crypto" / "cleaned"


def clean_ethusdt_5min_data(
    raw_data_path: Path,
) -> pd.DataFrame:
    try:
        cleaned_data: pd.DataFrame = pd.read_csv(
            raw_data_path,
        )

    except (OSError, pd.errors.ParserError) as error:
        raise RuntimeError("Failed to read raw ETHUSDT " "5-minute data.") from error

    datetime_columns = [
        "datetime",
        "close_datetime",
    ]

    for column in datetime_columns:
        cleaned_data[column] = pd.to_datetime(
            cleaned_data[column],
            utc=True,
            errors="coerce",
        )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume",
        "trade_count",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    original_rows = len(cleaned_data)

    cleaned_data = cleaned_data.dropna(
        subset=[
            "datetime",
            "open",
            "high",
            "low",
            "close",
        ]
    )

    cleaned_data = cleaned_data.drop_duplicates(
        subset=["datetime"],
        keep="last",
    )

    valid_ohlc = (
        cleaned_data["high"] >= cleaned_data[["open", "close", "low"]].max(axis=1)
    ) & (cleaned_data["low"] <= cleaned_data[["open", "close", "high"]].min(axis=1))

    nonnegative_values = (
        (cleaned_data["volume"] >= 0)
        & (cleaned_data["quote_volume"] >= 0)
        & (cleaned_data["trade_count"] >= 0)
        & (cleaned_data["taker_buy_base_volume"] >= 0)
        & (cleaned_data["taker_buy_quote_volume"] >= 0)
    )

    cleaned_data = cleaned_data[valid_ohlc & nonnegative_values]

    cleaned_data["trade_count"] = cleaned_data["trade_count"].astype("int64")

    cleaned_data = cleaned_data.sort_values("datetime").reset_index(drop=True)

    cleaned_rows = len(cleaned_data)

    print(f"Original rows: {original_rows}")
    print(f"Cleaned rows: {cleaned_rows}")
    print("Removed rows: " f"{original_rows - cleaned_rows}")

    if not cleaned_data.empty:
        print("Start datetime: " f"{cleaned_data['datetime'].min()}")
        print("End datetime: " f"{cleaned_data['datetime'].max()}")

    return cleaned_data


def store_cleaned_ethusdt_data(
    cleaned_data: pd.DataFrame,
) -> None:
    CLEANED_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CLEANED_DATA_DIRECTORY / "cleaned_ETHUSDT_5min_binance_us.csv"

    try:
        cleaned_data.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

    except OSError as error:
        raise RuntimeError(
            "Failed to store cleaned ETHUSDT " "5-minute data."
        ) from error

    print(f"Cleaned data stored: {output_path}")


if __name__ == "__main__":
    ethusdt_data = clean_ethusdt_5min_data(RAW_DATA_PATH)

    print(ethusdt_data.head())
    print(ethusdt_data.tail())

    store_cleaned_ethusdt_data(ethusdt_data)
