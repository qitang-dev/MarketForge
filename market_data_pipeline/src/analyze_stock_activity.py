from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_ROOT = PROJECT_ROOT / "data" / "analysis" / "activity_analysis"

INDIVIDUAL_OUTPUT_DIRECTORY = OUTPUT_ROOT / "individual"

SUMMARY_OUTPUT_DIRECTORY = OUTPUT_ROOT / "summary"

COMBINED_SUMMARY_OUTPUT_PATH = OUTPUT_ROOT / "combined_activity_summary.csv"

PROCESSING_SUMMARY_OUTPUT_PATH = OUTPUT_ROOT / "processing_summary.csv"


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


def get_input_path(
    stock_code: str,
) -> Path:
    stock_data_indicators_path = (
        PROJECT_ROOT
        / "data"
        / "indicators"
        / f"cleaned_{stock_code}_with_ma_columns.csv"
    )

    if not stock_data_indicators_path.exists():
        raise FileNotFoundError(
            f"Indicator data not found for "
            f"{stock_code}: "
            f"{stock_data_indicators_path}"
        )

    return stock_data_indicators_path


def clean_indicator_data(
    input_path: Path,
    stock_code: str,
) -> pd.DataFrame:
    data = pd.read_csv(
        input_path,
        encoding="utf-8-sig",
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    # Remove index-like columns such as:
    # "", "unnamed: 0"
    index_like_columns = [
        column
        for column in data.columns
        if (column == "" or column.startswith("unnamed"))
    ]

    if index_like_columns:
        data = data.drop(columns=index_like_columns)

    required_columns = [
        "date",
        "open",
        "close",
        "high",
        "low",
        "volume",
        "turnover",
        "amount",
        "ma_3",
        "ma_5",
        "ma_7",
        "ma_10",
        "ma_20",
        "ma_21",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing required columns for "
            f"{stock_code}: "
            f"{missing_columns}. "
            f"Available columns: "
            f"{data.columns.tolist()}"
        )

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce",
    )

    numeric_columns = [
        "open",
        "close",
        "high",
        "low",
        "volume",
        "turnover",
        "amount",
        "ma_3",
        "ma_5",
        "ma_7",
        "ma_10",
        "ma_20",
        "ma_21",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "date",
            "open",
            "close",
            "high",
            "low",
            "volume",
        ]
    )

    data = data.drop_duplicates(
        subset=["date"],
        keep="last",
    )

    data = data.sort_values(by="date").reset_index(drop=True)

    data["stock_code"] = stock_code

    return data


def calculate_activity_features(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    # Previous close
    result["previous_close"] = result["close"].shift(1)

    # Daily return
    result["daily_return"] = result["close"] / result["previous_close"] - 1

    # Absolute daily return
    result["absolute_return"] = result["daily_return"].abs()

    # Intraday price range
    result["intraday_range"] = (result["high"] - result["low"]) / result[
        "previous_close"
    ]

    # Historical volume baselines.
    # shift(1) ensures today's volume is not
    # included in its own reference average.
    result["volume_ma_5"] = (
        result["volume"]
        .shift(1)
        .rolling(
            window=5,
            min_periods=5,
        )
        .mean()
    )

    result["volume_ma_20"] = (
        result["volume"]
        .shift(1)
        .rolling(
            window=20,
            min_periods=20,
        )
        .mean()
    )

    # Volume ratios
    result["volume_ratio_5"] = result["volume"] / result["volume_ma_5"]

    result["volume_ratio_20"] = result["volume"] / result["volume_ma_20"]

    # Historical 20-day volatility
    result["volatility_20"] = (
        result["daily_return"]
        .shift(1)
        .rolling(
            window=20,
            min_periods=20,
        )
        .std()
    )

    # Historical turnover baseline
    result["turnover_ma_20"] = (
        result["turnover"]
        .shift(1)
        .rolling(
            window=20,
            min_periods=20,
        )
        .mean()
    )

    result["turnover_ratio_20"] = result["turnover"] / result["turnover_ma_20"]

    # Price relative to existing MA20
    result["price_to_ma20"] = result["close"] / result["ma_20"] - 1

    # Short-term MA relative to MA20
    result["ma5_to_ma20"] = result["ma_5"] / result["ma_20"] - 1

    # Change in MA20 over five trading days
    result["ma20_slope_5"] = result["ma_20"] / result["ma_20"].shift(5) - 1

    # Moving-average compression / dispersion
    ma_columns = [
        "ma_3",
        "ma_5",
        "ma_7",
        "ma_10",
        "ma_20",
        "ma_21",
    ]

    result["ma_max"] = result[ma_columns].max(axis=1)

    result["ma_min"] = result[ma_columns].min(axis=1)

    result["ma_spread"] = result["ma_max"] / result["ma_min"] - 1

    return result


def identify_activity_events(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    # Absolute daily move >= 5%
    result["large_move"] = result["absolute_return"] >= 0.05

    result["large_up_move"] = result["daily_return"] >= 0.05

    result["large_down_move"] = result["daily_return"] <= -0.05

    # Today's volume >= 2 × previous
    # 20-day average volume
    result["volume_surge"] = result["volume_ratio_20"] >= 2.0

    # Absolute turnover threshold
    result["high_turnover_day"] = result["turnover"] >= 10.0

    # Relative turnover threshold
    result["turnover_surge"] = result["turnover_ratio_20"] >= 2.0

    # Intraday range >= 8%
    result["high_volatility_day"] = result["intraday_range"] >= 0.08

    return result


def calculate_event_rate(
    series: pd.Series,
) -> float:
    valid_series = series.dropna().astype(bool)

    if valid_series.empty:
        return float("nan")

    return float(valid_series.mean())


def classify_activity_style(
    average_turnover: float,
    annualized_volatility: float,
    large_move_rate: float,
    volume_surge_rate: float,
) -> str:
    score = 0

    # Turnover
    if pd.notna(average_turnover):
        if average_turnover >= 8.0:
            score += 2
        elif average_turnover >= 4.0:
            score += 1

    # Volatility
    if pd.notna(annualized_volatility):
        if annualized_volatility >= 0.50:
            score += 2
        elif annualized_volatility >= 0.30:
            score += 1

    # Large daily moves
    if pd.notna(large_move_rate):
        if large_move_rate >= 0.10:
            score += 2
        elif large_move_rate >= 0.05:
            score += 1

    # Volume surges
    if pd.notna(volume_surge_rate):
        if volume_surge_rate >= 0.08:
            score += 2
        elif volume_surge_rate >= 0.04:
            score += 1

    if score >= 6:
        return "highly_active"

    if score >= 4:
        return "active"

    if score >= 2:
        return "moderately_active"

    return "quiet"


def build_activity_summary(
    data: pd.DataFrame,
    stock_code: str,
) -> pd.DataFrame:
    valid_returns = data["daily_return"].dropna()

    annualized_volatility = valid_returns.std() * np.sqrt(252)

    average_turnover = data["turnover"].mean()

    large_move_rate = calculate_event_rate(data["large_move"])

    volume_surge_rate = calculate_event_rate(data["volume_surge"])

    turnover_surge_rate = calculate_event_rate(data["turnover_surge"])

    high_volatility_rate = calculate_event_rate(data["high_volatility_day"])

    summary_record = {
        "stock_code": stock_code,
        "start_date": (data["date"].min()),
        "end_date": (data["date"].max()),
        "trading_days": len(data),
        # Return and volatility
        "average_daily_return": (valid_returns.mean()),
        "average_absolute_return": (data["absolute_return"].mean()),
        "annualized_volatility": (annualized_volatility),
        # Intraday movement
        "average_intraday_range": (data["intraday_range"].mean()),
        "maximum_intraday_range": (data["intraday_range"].max()),
        # Turnover
        "average_turnover": (average_turnover),
        "median_turnover": (data["turnover"].median()),
        "maximum_turnover": (data["turnover"].max()),
        "average_turnover_ratio_20": (data["turnover_ratio_20"].mean()),
        "maximum_turnover_ratio_20": (data["turnover_ratio_20"].max()),
        # Volume
        "average_volume_ratio_20": (data["volume_ratio_20"].mean()),
        "maximum_volume_ratio_20": (data["volume_ratio_20"].max()),
        # Large moves
        "large_move_count": int(data["large_move"].sum()),
        "large_up_move_count": int(data["large_up_move"].sum()),
        "large_down_move_count": int(data["large_down_move"].sum()),
        "large_move_rate": (large_move_rate),
        # Volume events
        "volume_surge_count": int(data["volume_surge"].sum()),
        "volume_surge_rate": (volume_surge_rate),
        # Turnover events
        "high_turnover_day_count": int(data["high_turnover_day"].sum()),
        "turnover_surge_count": int(data["turnover_surge"].sum()),
        "turnover_surge_rate": (turnover_surge_rate),
        # Intraday volatility events
        "high_volatility_day_count": int(data["high_volatility_day"].sum()),
        "high_volatility_day_rate": (high_volatility_rate),
        # Existing MA-derived features
        "average_price_to_ma20": (data["price_to_ma20"].mean()),
        "maximum_price_above_ma20": (data["price_to_ma20"].max()),
        "maximum_price_below_ma20": (data["price_to_ma20"].min()),
        "average_ma5_to_ma20": (data["ma5_to_ma20"].mean()),
        "average_ma20_slope_5": (data["ma20_slope_5"].mean()),
        "average_ma_spread": (data["ma_spread"].mean()),
        "median_ma_spread": (data["ma_spread"].median()),
        "minimum_ma_spread": (data["ma_spread"].min()),
    }

    summary_record["activity_style"] = classify_activity_style(
        average_turnover=average_turnover,
        annualized_volatility=(annualized_volatility),
        large_move_rate=large_move_rate,
        volume_surge_rate=(volume_surge_rate),
    )

    return pd.DataFrame([summary_record])


def store_individual_analysis(
    stock_code: str,
    data: pd.DataFrame,
) -> Path:
    INDIVIDUAL_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = INDIVIDUAL_OUTPUT_DIRECTORY / f"{stock_code}_activity_analysis.csv"

    data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def store_summary(
    stock_code: str,
    summary_data: pd.DataFrame,
) -> Path:
    SUMMARY_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = SUMMARY_OUTPUT_DIRECTORY / f"{stock_code}_activity_summary.csv"

    summary_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def build_processing_record(
    stock_code: str,
    status: str,
    rows: int = 0,
    error_message: str = "",
) -> dict:
    return {
        "stock_code": stock_code,
        "status": status,
        "rows": rows,
        "error_message": error_message,
    }


def process_all_stocks() -> None:
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

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

        try:
            input_path = get_input_path(stock_code=stock_code)

            print(f"[INPUT] {input_path}")

            data = clean_indicator_data(
                input_path=input_path,
                stock_code=stock_code,
            )

            data = calculate_activity_features(data=data)

            data = identify_activity_events(data=data)

            summary_data = build_activity_summary(
                data=data,
                stock_code=stock_code,
            )

            individual_output_path = store_individual_analysis(
                stock_code=stock_code,
                data=data,
            )

            summary_output_path = store_summary(
                stock_code=stock_code,
                summary_data=summary_data,
            )

            all_summary_data.append(summary_data)

            processing_records.append(
                build_processing_record(
                    stock_code=stock_code,
                    status="success",
                    rows=len(data),
                )
            )

            print(f"[SUCCESS] Large moves: " f"{int(data['large_move'].sum())}")

            print(f"[SUCCESS] Volume surges: " f"{int(data['volume_surge'].sum())}")

            print(f"[SUCCESS] Turnover surges: " f"{int(data['turnover_surge'].sum())}")

            print(
                f"[SUCCESS] High-volatility days: "
                f"{int(data['high_volatility_day'].sum())}"
            )

            print(
                f"[SUCCESS] Activity style: " f"{summary_data.loc[0, 'activity_style']}"
            )

            print(f"[SAVED] " f"{individual_output_path}")

            print(f"[SAVED] " f"{summary_output_path}")

        except Exception as error:
            processing_records.append(
                build_processing_record(
                    stock_code=stock_code,
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED] " f"{stock_code}: " f"{error}")

    if all_summary_data:
        combined_summary_data = pd.concat(
            all_summary_data,
            ignore_index=True,
        )

        combined_summary_data = combined_summary_data.sort_values(
            by="annualized_volatility",
            ascending=False,
        ).reset_index(drop=True)

        combined_summary_data.to_csv(
            COMBINED_SUMMARY_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(
            f"\n[SAVED] Combined activity summary: " f"{COMBINED_SUMMARY_OUTPUT_PATH}"
        )

        print("\n========== " "ACTIVITY SUMMARY " "==========")

        display_columns = [
            "stock_code",
            "average_turnover",
            "annualized_volatility",
            "average_intraday_range",
            "large_move_count",
            "volume_surge_count",
            "turnover_surge_count",
            "high_volatility_day_count",
            "average_ma_spread",
            "activity_style",
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

    print("\n========== " "PROCESSING RESULT " "==========")

    print(f"Total stocks: " f"{total_stocks}")

    print(f"Successful: " f"{success_count}")

    print(f"Failed: " f"{failed_count}")


if __name__ == "__main__":
    process_all_stocks()
