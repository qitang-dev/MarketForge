from pathlib import Path
import time

import pandas as pd
import requests

API_URL = "https://api.binance.us/api/v3/klines"

KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trade_count",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "ignore",
]

INTERVAL_MILLISECONDS = 5 * 60 * 1000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "crypto" / "raw"


def request_kline_batch(
    start_time_ms: int,
    end_time_ms: int,
    max_retries: int = 5,
) -> list:
    parameters = {
        "symbol": "ETHUSDT",
        "interval": "5m",
        "startTime": start_time_ms,
        "endTime": end_time_ms,
        "limit": 1000,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                API_URL,
                params=parameters,
                timeout=30,
            )

            if response.status_code == 429:
                retry_after = int(
                    response.headers.get(
                        "Retry-After",
                        5,
                    )
                )

                print("Rate limit reached. " f"Waiting {retry_after} seconds...")

                time.sleep(retry_after)
                continue

            response.raise_for_status()

            raw_data = response.json()

            if not isinstance(raw_data, list):
                raise RuntimeError(
                    "Unexpected response format " f"from Binance.US: {raw_data}"
                )

            return raw_data

        except requests.RequestException as error:
            if attempt == max_retries:
                raise RuntimeError(
                    "Failed to fetch ETHUSDT " "5-minute data from Binance.US."
                ) from error

            waiting_seconds = attempt * 2

            print(
                f"Request failed on attempt "
                f"{attempt}/{max_retries}. "
                f"Waiting {waiting_seconds} seconds..."
            )

            time.sleep(waiting_seconds)

    return []


def fetch_ethusdt_5min_two_years() -> pd.DataFrame:
    end_datetime = pd.Timestamp.now(tz="UTC").floor("5min")

    start_datetime = end_datetime - pd.DateOffset(years=2)

    start_time_ms = int(start_datetime.timestamp() * 1000)

    end_time_ms = int(end_datetime.timestamp() * 1000)

    current_start_time_ms = start_time_ms
    all_raw_data = []
    request_count = 0

    print("Fetching ETHUSDT 5-minute data:")
    print(f"Start: {start_datetime}")
    print(f"End:   {end_datetime}")

    while current_start_time_ms <= end_time_ms:
        batch_data = request_kline_batch(
            start_time_ms=current_start_time_ms,
            end_time_ms=end_time_ms,
        )

        request_count += 1

        if len(batch_data) == 0:
            print("No additional data returned.")
            break

        all_raw_data.extend(batch_data)

        last_open_time_ms = int(batch_data[-1][0])

        batch_start = pd.to_datetime(
            batch_data[0][0],
            unit="ms",
            utc=True,
        )

        batch_end = pd.to_datetime(
            last_open_time_ms,
            unit="ms",
            utc=True,
        )

        print(
            f"Request {request_count}: "
            f"{len(batch_data)} rows, "
            f"{batch_start} -> {batch_end}"
        )

        next_start_time_ms = last_open_time_ms + INTERVAL_MILLISECONDS

        if next_start_time_ms <= current_start_time_ms:
            raise RuntimeError("Pagination did not advance.")

        current_start_time_ms = next_start_time_ms

        if len(batch_data) < 1000:
            break

        time.sleep(0.1)

    if len(all_raw_data) == 0:
        return pd.DataFrame(columns=KLINE_COLUMNS)

    data = pd.DataFrame(
        all_raw_data,
        columns=KLINE_COLUMNS,
    )

    data["datetime"] = pd.to_datetime(
        data["open_time"],
        unit="ms",
        utc=True,
    )

    data["close_datetime"] = pd.to_datetime(
        data["close_time"],
        unit="ms",
        utc=True,
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
            ]
        )
        .drop_duplicates(
            subset=["datetime"],
            keep="last",
        )
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    selected_columns = [
        "datetime",
        "close_datetime",
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

    data = data[selected_columns]

    print()
    print("Fetch completed.")
    print(f"Requests: {request_count}")
    print(f"Rows: {len(data)}")
    print(f"Start: {data['datetime'].min()}")
    print(f"End:   {data['datetime'].max()}")

    return data


def store_ethusdt_5min_data(
    data: pd.DataFrame,
) -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIRECTORY / "ETHUSDT_5min_binance_us.csv"

    try:
        data.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

    except OSError as error:
        raise RuntimeError("Failed to store ETHUSDT " "5-minute data.") from error

    print(f"Stored data: {output_path}")


if __name__ == "__main__":
    ethusdt_data = fetch_ethusdt_5min_two_years()

    print(ethusdt_data.head())
    print(ethusdt_data.tail())

    store_ethusdt_5min_data(ethusdt_data)
