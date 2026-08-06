from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "unadjusted"
    / "cleaned_sz002067_daily_unadjusted_tx.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "analysis"
    / "limit_analysis"
    / "individual"
    / "sz002067_limit_analysis.csv"
)


def round_stock_price(
    price: float,
) -> float:
    return float(
        Decimal(str(price)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    )


def get_limit_rate(
    stock_code: str,
    is_st: bool = False,
) -> float:
    numeric_code = stock_code[-6:]

    if is_st:
        return 0.05

    if numeric_code.startswith("300"):
        return 0.20

    return 0.10


def calculate_limit_prices(
    data: pd.DataFrame,
    stock_code: str,
) -> pd.DataFrame:
    result = data.copy()

    limit_rate = get_limit_rate(
        stock_code=stock_code,
        is_st=False,
    )

    result["limit_rate"] = limit_rate

    result["previous_close"] = result["close"].shift(1)

    result["limit_up_price"] = result["previous_close"].map(
        lambda price: (
            round_stock_price(price * (1 + limit_rate)) if pd.notna(price) else np.nan
        )
    )

    result["limit_down_price"] = result["previous_close"].map(
        lambda price: (
            round_stock_price(price * (1 - limit_rate)) if pd.notna(price) else np.nan
        )
    )

    return result


def identify_limit_events(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    tolerance = 0.001

    result["touched_limit_up"] = result["high"] >= result["limit_up_price"] - tolerance

    result["limit_up"] = np.isclose(
        result["close"],
        result["limit_up_price"],
        atol=tolerance,
        rtol=0,
    )

    result["limit_down"] = np.isclose(
        result["close"],
        result["limit_down_price"],
        atol=tolerance,
        rtol=0,
    )

    result["one_word_limit_up"] = (
        np.isclose(
            result["open"],
            result["limit_up_price"],
            atol=tolerance,
            rtol=0,
        )
        & np.isclose(
            result["high"],
            result["limit_up_price"],
            atol=tolerance,
            rtol=0,
        )
        & np.isclose(
            result["low"],
            result["limit_up_price"],
            atol=tolerance,
            rtol=0,
        )
        & np.isclose(
            result["close"],
            result["limit_up_price"],
            atol=tolerance,
            rtol=0,
        )
    )

    result["failed_limit_up"] = result["touched_limit_up"] & ~result["limit_up"]

    return result


def calculate_consecutive_limit_up(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    group_id = result["limit_up"].ne(result["limit_up"].shift()).cumsum()

    result["consecutive_limit_up_days"] = (
        result["limit_up"].astype(int).groupby(group_id).cumsum()
    )

    return result


def calculate_post_limit_returns(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["next_open_return"] = result["open"].shift(-1) / result["close"] - 1

    result["next_close_return"] = result["close"].shift(-1) / result["close"] - 1

    result["return_after_3_days"] = result["close"].shift(-3) / result["close"] - 1

    result["return_after_5_days"] = result["close"].shift(-5) / result["close"] - 1

    return result


def assign_event_type(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["event_type"] = "normal"

    result.loc[
        result["limit_up"],
        "event_type",
    ] = "limit_up"

    result.loc[
        result["one_word_limit_up"],
        "event_type",
    ] = "one_word_limit_up"

    result.loc[
        result["failed_limit_up"],
        "event_type",
    ] = "failed_limit_up"

    return result


def analyze_limit_events(
    stock_code: str,
    input_path: Path,
) -> pd.DataFrame:
    data = pd.read_csv(
        input_path,
        encoding="utf-8-sig",
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce",
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "turnover_rate",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    data = data.dropna(
        subset=[
            "date",
            "open",
            "high",
            "low",
            "close",
        ]
    )

    data = data.sort_values(by="date").reset_index(drop=True)

    data["stock_code"] = stock_code

    data = calculate_limit_prices(
        data=data,
        stock_code=stock_code,
    )

    data = identify_limit_events(data=data)

    data = calculate_consecutive_limit_up(data=data)

    data = calculate_post_limit_returns(data=data)

    data = assign_event_type(data=data)

    return data


def main() -> None:
    stock_code = "sz002067"

    analyzed_data = analyze_limit_events(
        stock_code=stock_code,
        input_path=INPUT_PATH,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    analyzed_data.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    event_data = analyzed_data[analyzed_data["event_type"] != "normal"].copy()

    print("\n========== LIMIT EVENT SUMMARY ==========")

    print(f"Stock code: {stock_code}")

    print(f"Limit-up count: " f"{int(analyzed_data['limit_up'].sum())}")

    print(
        f"One-word limit-up count: " f"{int(analyzed_data['one_word_limit_up'].sum())}"
    )

    print(f"Failed limit-up count: " f"{int(analyzed_data['failed_limit_up'].sum())}")

    print(
        f"Maximum consecutive limit-up days: "
        f"{int(analyzed_data['consecutive_limit_up_days'].max())}"
    )

    print("\nLimit events:")

    display_columns = [
        "date",
        "event_type",
        "close",
        "limit_up_price",
        "consecutive_limit_up_days",
        "next_open_return",
        "next_close_return",
        "return_after_3_days",
        "return_after_5_days",
    ]

    print(event_data[display_columns].to_string(index=False))

    print(f"\n[SAVED] {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
