from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIRECTORY = PROJECT_ROOT / "data" / "cleaned" / "unadjusted"

OUTPUT_ROOT = PROJECT_ROOT / "data" / "analysis" / "limit_analysis"

INDIVIDUAL_OUTPUT_DIRECTORY = OUTPUT_ROOT / "individual"

EVENT_OUTPUT_DIRECTORY = OUTPUT_ROOT / "events"

SUMMARY_OUTPUT_DIRECTORY = OUTPUT_ROOT / "summary"

COMBINED_EVENT_OUTPUT_PATH = OUTPUT_ROOT / "combined_limit_events.csv"

COMBINED_SUMMARY_OUTPUT_PATH = OUTPUT_ROOT / "combined_limit_summary.csv"

PROCESSING_SUMMARY_OUTPUT_PATH = OUTPUT_ROOT / "processing_summary.csv"

"""
ST RULE:
STOCK CODE STARTING WITH 300: 20%
OTHERS: 10%
ALL STOCK IS NOT 'ST' BY DEFAULT
"""

A_STOCK_CODES = [
    "sz002067",
    "sz002600",
    "sz002230",
    "sh600763",
    "sh603259",
    "sh603799",
    "sh601012",
    "sh600438",
    "sz002361",
    "sh601500",
    "sh600231",
    "sz300274",
    "sh601636",
    "sz002129",
    "sz000100",
    "sz300433",
]


def normalize_stock_code(
    stock_code: str,
) -> str:
    normalized_code = stock_code.strip().lower()

    if (
        len(normalized_code) != 8
        or normalized_code[:2]
        not in {
            "sh",
            "sz",
            "bj",
        }
        or not normalized_code[2:].isdigit()
    ):
        raise ValueError(
            f"Invalid stock code: {stock_code}. "
            "Expected formats such as "
            "'sz002067' or 'sh600763'."
        )

    return normalized_code


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


def clean_daily_data(
    input_path: Path,
    stock_code: str,
) -> pd.DataFrame:
    data = pd.read_csv(
        input_path,
        encoding="utf-8-sig",
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    column_aliases = {
        "日期": "date",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover_rate",
    }

    data = data.rename(
        columns={
            column: column_aliases[column]
            for column in data.columns
            if column in column_aliases
        }
    )

    required_columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing required columns for "
            f"{stock_code}: {missing_columns}. "
            f"Available columns: "
            f"{data.columns.tolist()}"
        )

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

    data = data.drop_duplicates(
        subset=["date"],
        keep="last",
    )

    data = data.sort_values(by="date").reset_index(drop=True)

    data["stock_code"] = stock_code

    return data


def calculate_limit_prices(
    data: pd.DataFrame,
    stock_code: str,
) -> pd.DataFrame:
    result = data.copy()

    limit_rate = get_limit_rate(
        stock_code=stock_code,
        is_st=False,
    )

    result["is_st"] = False
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

    valid_limit_price = result["limit_up_price"].notna()

    result["touched_limit_up"] = valid_limit_price & (
        result["high"] >= result["limit_up_price"] - tolerance
    )

    result["limit_up"] = valid_limit_price & np.isclose(
        result["close"],
        result["limit_up_price"],
        atol=tolerance,
        rtol=0,
    )

    result["limit_down"] = result["limit_down_price"].notna() & np.isclose(
        result["close"],
        result["limit_down_price"],
        atol=tolerance,
        rtol=0,
    )

    result["one_word_limit_up"] = (
        valid_limit_price
        & np.isclose(
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

    result["failed_limit_pullback"] = np.where(
        result["failed_limit_up"],
        (result["close"] / result["limit_up_price"] - 1),
        np.nan,
    )

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


def calculate_post_event_returns(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["next_open_return"] = result["open"].shift(-1) / result["close"] - 1

    result["next_close_return"] = result["close"].shift(-1) / result["close"] - 1

    result["close_return_after_3_days"] = (
        result["close"].shift(-3) / result["close"] - 1
    )

    result["close_return_after_5_days"] = (
        result["close"].shift(-5) / result["close"] - 1
    )

    future_high_5_days = pd.concat(
        [result["high"].shift(-offset) for offset in range(1, 6)],
        axis=1,
    ).max(
        axis=1,
        skipna=True,
    )

    future_low_5_days = pd.concat(
        [result["low"].shift(-offset) for offset in range(1, 6)],
        axis=1,
    ).min(
        axis=1,
        skipna=True,
    )

    result["maximum_return_within_5_days"] = future_high_5_days / result["close"] - 1

    result["maximum_drawdown_within_5_days"] = future_low_5_days / result["close"] - 1

    return result


def calculate_volume_features(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    if "volume" in result.columns:
        result["volume_ma_5"] = (
            result["volume"]
            .rolling(
                window=5,
                min_periods=1,
            )
            .mean()
        )

        result["volume_ratio_5"] = result["volume"] / result["volume_ma_5"]

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
    data = clean_daily_data(
        input_path=input_path,
        stock_code=stock_code,
    )

    data = calculate_limit_prices(
        data=data,
        stock_code=stock_code,
    )

    data = identify_limit_events(data=data)

    data = calculate_consecutive_limit_up(data=data)

    data = calculate_post_event_returns(data=data)

    data = calculate_volume_features(data=data)

    data = assign_event_type(data=data)

    return data


def extract_limit_events(
    data: pd.DataFrame,
) -> pd.DataFrame:
    event_data = data[data["limit_up"] | data["failed_limit_up"]].copy()

    preferred_columns = [
        "stock_code",
        "date",
        "event_type",
        "previous_close",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "turnover_rate",
        "volume_ratio_5",
        "limit_rate",
        "limit_up_price",
        "limit_down_price",
        "touched_limit_up",
        "limit_up",
        "one_word_limit_up",
        "failed_limit_up",
        "failed_limit_pullback",
        "consecutive_limit_up_days",
        "next_open_return",
        "next_close_return",
        "close_return_after_3_days",
        "close_return_after_5_days",
        "maximum_return_within_5_days",
        "maximum_drawdown_within_5_days",
    ]

    existing_columns = [
        column for column in preferred_columns if column in event_data.columns
    ]

    return event_data[existing_columns].reset_index(drop=True)


def calculate_positive_rate(
    series: pd.Series,
) -> float:
    valid_series = series.dropna()

    if valid_series.empty:
        return float("nan")

    return float(valid_series.gt(0).mean())


def build_limit_summary(
    data: pd.DataFrame,
    stock_code: str,
) -> pd.DataFrame:
    limit_up_data = data[data["limit_up"]].copy()

    failed_limit_data = data[data["failed_limit_up"]].copy()

    touched_limit_up_count = int(data["touched_limit_up"].sum())

    limit_up_count = int(data["limit_up"].sum())

    failed_limit_up_count = int(data["failed_limit_up"].sum())

    failed_limit_up_rate = (
        failed_limit_up_count / touched_limit_up_count
        if touched_limit_up_count > 0
        else float("nan")
    )

    first_limit_count = int((data["consecutive_limit_up_days"] == 1).sum())

    second_limit_count = int((data["consecutive_limit_up_days"] == 2).sum())

    third_or_more_limit_count = int((data["consecutive_limit_up_days"] >= 3).sum())

    summary_record = {
        "stock_code": stock_code,
        "start_date": data["date"].min(),
        "end_date": data["date"].max(),
        "trading_days": len(data),
        "touched_limit_up_count": (touched_limit_up_count),
        "limit_up_count": limit_up_count,
        "one_word_limit_up_count": int(data["one_word_limit_up"].sum()),
        "failed_limit_up_count": (failed_limit_up_count),
        "failed_limit_up_rate": (failed_limit_up_rate),
        "limit_down_count": int(data["limit_down"].sum()),
        "first_limit_count": (first_limit_count),
        "second_limit_count": (second_limit_count),
        "third_or_more_limit_count": (third_or_more_limit_count),
        "maximum_consecutive_limit_up_days": int(
            data["consecutive_limit_up_days"].max()
        ),
        "average_next_open_return": (limit_up_data["next_open_return"].mean()),
        "median_next_open_return": (limit_up_data["next_open_return"].median()),
        "average_next_close_return": (limit_up_data["next_close_return"].mean()),
        "median_next_close_return": (limit_up_data["next_close_return"].median()),
        "average_close_return_after_3_days": (
            limit_up_data["close_return_after_3_days"].mean()
        ),
        "median_close_return_after_3_days": (
            limit_up_data["close_return_after_3_days"].median()
        ),
        "average_close_return_after_5_days": (
            limit_up_data["close_return_after_5_days"].mean()
        ),
        "median_close_return_after_5_days": (
            limit_up_data["close_return_after_5_days"].median()
        ),
        "positive_next_close_rate": (
            calculate_positive_rate(limit_up_data["next_close_return"])
        ),
        "positive_3_day_rate": (
            calculate_positive_rate(limit_up_data["close_return_after_3_days"])
        ),
        "positive_5_day_rate": (
            calculate_positive_rate(limit_up_data["close_return_after_5_days"])
        ),
        "average_maximum_return_within_5_days": (
            limit_up_data["maximum_return_within_5_days"].mean()
        ),
        "average_maximum_drawdown_within_5_days": (
            limit_up_data["maximum_drawdown_within_5_days"].mean()
        ),
        "average_failed_limit_pullback": (
            failed_limit_data["failed_limit_pullback"].mean()
        ),
    }

    if "turnover_rate" in data.columns:
        summary_record["average_limit_up_turnover_rate"] = limit_up_data[
            "turnover_rate"
        ].mean()

        summary_record["average_failed_limit_turnover_rate"] = failed_limit_data[
            "turnover_rate"
        ].mean()

    if "volume_ratio_5" in data.columns:
        summary_record["average_limit_up_volume_ratio_5"] = limit_up_data[
            "volume_ratio_5"
        ].mean()

        summary_record["average_failed_limit_volume_ratio_5"] = failed_limit_data[
            "volume_ratio_5"
        ].mean()

    return pd.DataFrame([summary_record])


def store_individual_analysis(
    stock_code: str,
    analyzed_data: pd.DataFrame,
) -> Path:
    INDIVIDUAL_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = INDIVIDUAL_OUTPUT_DIRECTORY / f"{stock_code}_limit_analysis.csv"

    analyzed_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def store_event_data(
    stock_code: str,
    event_data: pd.DataFrame,
) -> Path:
    EVENT_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = EVENT_OUTPUT_DIRECTORY / f"{stock_code}_limit_events.csv"

    event_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def store_summary_data(
    stock_code: str,
    summary_data: pd.DataFrame,
) -> Path:
    SUMMARY_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = SUMMARY_OUTPUT_DIRECTORY / f"{stock_code}_limit_summary.csv"

    summary_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def build_processing_record(
    stock_code: str,
    status: str,
    input_path: Path | None = None,
    analyzed_data: pd.DataFrame | None = None,
    error_message: str = "",
) -> dict:
    if analyzed_data is None:
        analyzed_data = pd.DataFrame()

    return {
        "stock_code": stock_code,
        "status": status,
        "input_path": (str(input_path) if input_path is not None else ""),
        "rows": len(analyzed_data),
        "limit_up_count": (
            int(analyzed_data["limit_up"].sum())
            if (not analyzed_data.empty and "limit_up" in analyzed_data.columns)
            else 0
        ),
        "failed_limit_up_count": (
            int(analyzed_data["failed_limit_up"].sum())
            if (not analyzed_data.empty and "failed_limit_up" in analyzed_data.columns)
            else 0
        ),
        "error_message": error_message,
    }


def process_all_stocks() -> None:
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_event_data: list[pd.DataFrame] = []
    all_summary_data: list[pd.DataFrame] = []
    processing_records: list[dict] = []

    total_stocks = len(A_STOCK_CODES)

    for index, stock_code in enumerate(
        A_STOCK_CODES,
        start=1,
    ):
        print(
            f"\n========== " f"{index}/{total_stocks} " f"{stock_code} " f"=========="
        )

        input_path: Path | None = None

        try:
            normalized_code = normalize_stock_code(stock_code)

            input_path = (
                INPUT_DIRECTORY / f"cleaned_{normalized_code}_daily_unadjusted_tx.csv"
            )

            print(f"[INPUT] {input_path}")

            analyzed_data = analyze_limit_events(
                stock_code=stock_code,
                input_path=input_path,
            )

            event_data = extract_limit_events(data=analyzed_data)

            summary_data = build_limit_summary(
                data=analyzed_data,
                stock_code=stock_code,
            )

            individual_output_path = store_individual_analysis(
                stock_code=stock_code,
                analyzed_data=analyzed_data,
            )

            event_output_path = store_event_data(
                stock_code=stock_code,
                event_data=event_data,
            )

            summary_output_path = store_summary_data(
                stock_code=stock_code,
                summary_data=summary_data,
            )

            all_event_data.append(event_data)

            all_summary_data.append(summary_data)

            processing_records.append(
                build_processing_record(
                    stock_code=stock_code,
                    status="success",
                    input_path=input_path,
                    analyzed_data=analyzed_data,
                )
            )

            print(f"[SUCCESS] Limit-ups: " f"{int(analyzed_data['limit_up'].sum())}")

            print(
                f"[SUCCESS] Failed limit-ups: "
                f"{int(analyzed_data['failed_limit_up'].sum())}"
            )

            print(
                f"[SUCCESS] Maximum consecutive: "
                f"{int(analyzed_data['consecutive_limit_up_days'].max())}"
            )

            print(f"[SAVED] {individual_output_path}")

            print(f"[SAVED] {event_output_path}")

            print(f"[SAVED] {summary_output_path}")

        except Exception as error:
            processing_records.append(
                build_processing_record(
                    stock_code=stock_code,
                    status="failed",
                    input_path=input_path,
                    error_message=str(error),
                )
            )

            print(f"[FAILED] {stock_code}: {error}")

    if all_event_data:
        combined_event_data = pd.concat(
            all_event_data,
            ignore_index=True,
        )

        combined_event_data = combined_event_data.sort_values(
            by=[
                "stock_code",
                "date",
            ]
        ).reset_index(drop=True)

        combined_event_data.to_csv(
            COMBINED_EVENT_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"\n[SAVED] Combined events: " f"{COMBINED_EVENT_OUTPUT_PATH}")

    if all_summary_data:
        combined_summary_data = pd.concat(
            all_summary_data,
            ignore_index=True,
        )

        combined_summary_data = combined_summary_data.sort_values(
            by="stock_code"
        ).reset_index(drop=True)

        combined_summary_data.to_csv(
            COMBINED_SUMMARY_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"[SAVED] Combined summary: " f"{COMBINED_SUMMARY_OUTPUT_PATH}")

        print("\n========== COMBINED LIMIT SUMMARY ==========")

        display_columns = [
            "stock_code",
            "limit_up_count",
            "one_word_limit_up_count",
            "failed_limit_up_count",
            "failed_limit_up_rate",
            "maximum_consecutive_limit_up_days",
            "average_next_close_return",
            "average_close_return_after_3_days",
            "average_close_return_after_5_days",
            "positive_5_day_rate",
        ]

        print(combined_summary_data[display_columns].to_string(index=False))

    processing_summary = pd.DataFrame(processing_records)

    processing_summary.to_csv(
        PROCESSING_SUMMARY_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n[SAVED] Processing summary: " f"{PROCESSING_SUMMARY_OUTPUT_PATH}")

    success_count = int((processing_summary["status"] == "success").sum())

    failed_count = int((processing_summary["status"] == "failed").sum())

    print("\n========== PROCESSING RESULT ==========")

    print(f"Total stocks: {total_stocks}")

    print(f"Successful: {success_count}")

    print(f"Failed: {failed_count}")


if __name__ == "__main__":
    process_all_stocks()
