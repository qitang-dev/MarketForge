from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT / "data" / "crypto" / "cleaned" / "cleaned_ETHUSDT_5min_binance_us.csv"
)

OUTPUT_PATH = PROJECT_ROOT / "website" / "data" / "crypto" / "ETHUSDT_5min.json"

WEB_BAR_LIMIT = None


def prepare_ethusdt_web_data() -> None:
    try:
        data: pd.DataFrame = pd.read_csv(
            INPUT_PATH,
        )

    except (OSError, pd.errors.ParserError) as error:
        raise RuntimeError("Failed to read cleaned ETHUSDT data.") from error

    required_columns = [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    data["datetime"] = pd.to_datetime(
        data["datetime"],
        utc=True,
        errors="coerce",
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    data[numeric_columns] = data[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    data = (
        data.dropna(
            subset=[
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        )
        .drop_duplicates(
            subset=["datetime"],
            keep="last",
        )
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    if WEB_BAR_LIMIT is not None:
        data = data.tail(WEB_BAR_LIMIT).reset_index(drop=True)

    unix_epoch = pd.Timestamp(
        "1970-01-01",
        tz="UTC",
    )

    data["time"] = ((data["datetime"] - unix_epoch) // pd.Timedelta(seconds=1)).astype(
        "int64"
    )

    web_data = data[
        [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    web_data.to_json(
        OUTPUT_PATH,
        orient="records",
        force_ascii=False,
        double_precision=10,
    )

    print(f"Rows exported: {len(web_data)}")
    print(f"JSON stored: {OUTPUT_PATH}")


if __name__ == "__main__":
    prepare_ethusdt_web_data()
