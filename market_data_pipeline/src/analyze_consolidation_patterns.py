from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIRECTORY = (
    PROJECT_ROOT / "data" / "analysis" / "activity_analysis" / "individual"
)

OUTPUT_ROOT = PROJECT_ROOT / "data" / "analysis" / "consolidation_analysis"

INDIVIDUAL_OUTPUT_DIRECTORY = OUTPUT_ROOT / "individual"

PERIOD_OUTPUT_DIRECTORY = OUTPUT_ROOT / "periods"

SUMMARY_OUTPUT_DIRECTORY = OUTPUT_ROOT / "summary"

COMBINED_PERIOD_OUTPUT_PATH = OUTPUT_ROOT / "combined_consolidation_periods.csv"

COMBINED_SUMMARY_OUTPUT_PATH = OUTPUT_ROOT / "combined_consolidation_summary.csv"

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


ROLLING_WINDOW = 20

MAX_BOX_RANGE = 0.15
MAX_MA_SPREAD = 0.08
MAX_MA20_SLOPE = 0.03
MAX_VOLATILITY = 0.03

MIN_CONSOLIDATION_DAYS = 8


def get_input_path(
    stock_code: str,
) -> Path:
    input_path = INPUT_DIRECTORY / f"{stock_code}_activity_analysis.csv"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Activity analysis data not found " f"for {stock_code}: " f"{input_path}"
        )

    return input_path


def load_activity_data(
    input_path: Path,
    stock_code: str,
) -> pd.DataFrame:
    data = pd.read_csv(
        input_path,
        encoding="utf-8-sig",
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    required_columns = [
        "stock_code",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
        "daily_return",
        "intraday_range",
        "volatility_20",
        "ma20_slope_5",
        "ma_spread",
        "volume_ratio_20",
        "turnover_ratio_20",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing required columns for " f"{stock_code}: " f"{missing_columns}"
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
        "turnover",
        "daily_return",
        "intraday_range",
        "volatility_20",
        "ma20_slope_5",
        "ma_spread",
        "volume_ratio_20",
        "turnover_ratio_20",
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

    return data


def calculate_box_features(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["rolling_high_20"] = (
        result["high"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .max()
    )

    result["rolling_low_20"] = (
        result["low"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .min()
    )

    result["box_range_20"] = result["rolling_high_20"] / result["rolling_low_20"] - 1

    box_width = result["rolling_high_20"] - result["rolling_low_20"]

    result["price_position_in_box"] = np.where(
        box_width > 0,
        (result["close"] - result["rolling_low_20"]) / box_width,
        np.nan,
    )

    result["average_intraday_range_20"] = (
        result["intraday_range"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .mean()
    )

    result["average_turnover_20"] = (
        result["turnover"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .mean()
    )

    result["average_volume_ratio_20"] = (
        result["volume_ratio_20"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .mean()
    )

    result["average_turnover_ratio_20"] = (
        result["turnover_ratio_20"]
        .rolling(
            window=ROLLING_WINDOW,
            min_periods=ROLLING_WINDOW,
        )
        .mean()
    )

    return result


def identify_consolidation_days(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["flat_price_range"] = result["box_range_20"] <= MAX_BOX_RANGE

    result["compressed_ma"] = result["ma_spread"] <= MAX_MA_SPREAD

    result["flat_ma20"] = result["ma20_slope_5"].abs() <= MAX_MA20_SLOPE

    result["low_rolling_volatility"] = result["volatility_20"] <= MAX_VOLATILITY

    result["is_consolidation_candidate"] = (
        result["flat_price_range"]
        & result["compressed_ma"]
        & result["flat_ma20"]
        & result["low_rolling_volatility"]
    )

    return result


def assign_candidate_groups(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    candidate = result["is_consolidation_candidate"].fillna(False).astype(bool)

    group_id = candidate.ne(candidate.shift()).cumsum()

    result["candidate_group"] = np.where(
        candidate,
        group_id,
        np.nan,
    )

    return result


def split_consolidation_period(
    group: pd.DataFrame,
    max_box_range: float,
) -> list[pd.DataFrame]:
    group = group.sort_values(by="date").copy()

    periods: list[pd.DataFrame] = []

    current_indices: list[int] = []
    current_high: float | None = None
    current_low: float | None = None

    for row_index, row in group.iterrows():
        row_high = float(row["high"])

        row_low = float(row["low"])

        if not current_indices:
            current_indices = [row_index]

            current_high = row_high

            current_low = row_low

            continue

        new_high = max(
            current_high,
            row_high,
        )

        new_low = min(
            current_low,
            row_low,
        )

        new_box_range = new_high / new_low - 1

        if new_box_range <= max_box_range:
            current_indices.append(row_index)

            current_high = new_high

            current_low = new_low

        else:
            if len(current_indices) >= MIN_CONSOLIDATION_DAYS:
                periods.append(group.loc[current_indices].copy())

            current_indices = [row_index]

            current_high = row_high

            current_low = row_low

    if len(current_indices) >= MIN_CONSOLIDATION_DAYS:
        periods.append(group.loc[current_indices].copy())

    return periods


def build_fixed_box_periods(
    data: pd.DataFrame,
) -> list[pd.DataFrame]:
    candidate_data = data[data["is_consolidation_candidate"]].copy()

    if candidate_data.empty:
        return []

    fixed_box_periods: list[pd.DataFrame] = []

    grouped_data = candidate_data.groupby(
        "candidate_group",
        sort=True,
    )

    for _, group in grouped_data:
        split_periods = split_consolidation_period(
            group=group,
            max_box_range=(MAX_BOX_RANGE),
        )

        fixed_box_periods.extend(split_periods)

    return fixed_box_periods


def mark_valid_consolidation_days(
    data: pd.DataFrame,
    periods: list[pd.DataFrame],
) -> pd.DataFrame:
    result = data.copy()

    result["is_consolidation"] = False
    result["consolidation_group"] = np.nan

    for period_number, period in enumerate(
        periods,
        start=1,
    ):
        period_indices = period.index

        result.loc[
            period_indices,
            "is_consolidation",
        ] = True

        result.loc[
            period_indices,
            "consolidation_group",
        ] = period_number

    return result


def classify_consolidation_style(
    average_intraday_range: float,
    average_volume_ratio: float,
    average_turnover_ratio: float,
) -> str:
    score = 0

    if pd.notna(average_intraday_range):
        if average_intraday_range >= 0.05:
            score += 2

        elif average_intraday_range >= 0.03:
            score += 1

    if pd.notna(average_volume_ratio):
        if average_volume_ratio >= 1.50:
            score += 2

        elif average_volume_ratio >= 1.10:
            score += 1

    if pd.notna(average_turnover_ratio):
        if average_turnover_ratio >= 1.50:
            score += 2

        elif average_turnover_ratio >= 1.10:
            score += 1

    if score >= 4:
        return "active_consolidation"

    if score >= 2:
        return "moderate_consolidation"

    return "mild_consolidation"


def extract_consolidation_periods(
    data: pd.DataFrame,
    periods: list[pd.DataFrame],
    stock_code: str,
) -> pd.DataFrame:
    if not periods:
        return pd.DataFrame()

    period_records: list[dict] = []

    for period_number, period in enumerate(
        periods,
        start=1,
    ):
        period = period.sort_values(by="date").copy()

        start_index = period.index.min()

        end_index = period.index.max()

        start_date = period["date"].min()

        end_date = period["date"].max()

        duration = len(period)

        box_high = period["high"].max()

        box_low = period["low"].min()

        box_range = box_high / box_low - 1

        start_close = period.iloc[0]["close"]

        end_close = period.iloc[-1]["close"]

        period_return = end_close / start_close - 1

        average_intraday_range = period["intraday_range"].mean()

        average_turnover = period["turnover"].mean()

        average_volatility = period["volatility_20"].mean()

        average_ma_spread = period["ma_spread"].mean()

        average_volume_ratio = period["volume_ratio_20"].mean()

        average_turnover_ratio = period["turnover_ratio_20"].mean()

        style = classify_consolidation_style(
            average_intraday_range=(average_intraday_range),
            average_volume_ratio=(average_volume_ratio),
            average_turnover_ratio=(average_turnover_ratio),
        )

        next_day_return = np.nan
        breakout_direction = "unknown"

        if end_index + 1 < len(data):
            next_row = data.iloc[end_index + 1]

            next_close = next_row["close"]

            next_day_return = next_close / end_close - 1

            if next_close > box_high:
                breakout_direction = "up"

            elif next_close < box_low:
                breakout_direction = "down"

            else:
                breakout_direction = "inside"

        period_records.append(
            {
                "stock_code": (stock_code),
                "consolidation_group": (period_number),
                "start_date": (start_date),
                "end_date": (end_date),
                "duration_days": (duration),
                "start_close": (start_close),
                "end_close": (end_close),
                "period_return": (period_return),
                "box_high": (box_high),
                "box_low": (box_low),
                "box_range": (box_range),
                "average_intraday_range": (average_intraday_range),
                "average_turnover": (average_turnover),
                "average_volatility": (average_volatility),
                "average_ma_spread": (average_ma_spread),
                "average_volume_ratio_20": (average_volume_ratio),
                "average_turnover_ratio_20": (average_turnover_ratio),
                "consolidation_style": (style),
                "next_day_return": (next_day_return),
                "breakout_direction": (breakout_direction),
            }
        )

    return pd.DataFrame(period_records)


def build_consolidation_summary(
    data: pd.DataFrame,
    periods: pd.DataFrame,
    stock_code: str,
) -> pd.DataFrame:
    consolidation_days = int(data["is_consolidation"].sum())

    consolidation_day_rate = (
        consolidation_days / len(data) if len(data) > 0 else float("nan")
    )

    if periods.empty:
        summary_record = {
            "stock_code": stock_code,
            "consolidation_period_count": 0,
            "consolidation_days": (consolidation_days),
            "consolidation_day_rate": (consolidation_day_rate),
            "average_duration_days": (np.nan),
            "maximum_duration_days": (np.nan),
            "average_box_range": (np.nan),
            "average_period_return": (np.nan),
            "average_consolidation_turnover": (np.nan),
            "average_consolidation_volatility": (np.nan),
            "average_consolidation_ma_spread": (np.nan),
            "active_consolidation_count": 0,
            "moderate_consolidation_count": 0,
            "mild_consolidation_count": 0,
            "up_breakout_count": 0,
            "down_breakout_count": 0,
            "inside_after_period_count": 0,
        }

        return pd.DataFrame([summary_record])

    summary_record = {
        "stock_code": (stock_code),
        "consolidation_period_count": (len(periods)),
        "consolidation_days": (consolidation_days),
        "consolidation_day_rate": (consolidation_day_rate),
        "average_duration_days": (periods["duration_days"].mean()),
        "maximum_duration_days": int(periods["duration_days"].max()),
        "average_box_range": (periods["box_range"].mean()),
        "average_period_return": (periods["period_return"].mean()),
        "average_consolidation_turnover": (periods["average_turnover"].mean()),
        "average_consolidation_volatility": (periods["average_volatility"].mean()),
        "average_consolidation_ma_spread": (periods["average_ma_spread"].mean()),
        "active_consolidation_count": int(
            (periods["consolidation_style"] == "active_consolidation").sum()
        ),
        "moderate_consolidation_count": int(
            (periods["consolidation_style"] == "moderate_consolidation").sum()
        ),
        "mild_consolidation_count": int(
            (periods["consolidation_style"] == "mild_consolidation").sum()
        ),
        "up_breakout_count": int((periods["breakout_direction"] == "up").sum()),
        "down_breakout_count": int((periods["breakout_direction"] == "down").sum()),
        "inside_after_period_count": int(
            (periods["breakout_direction"] == "inside").sum()
        ),
    }

    return pd.DataFrame([summary_record])


def store_individual_analysis(
    stock_code: str,
    data: pd.DataFrame,
) -> Path:
    INDIVIDUAL_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        INDIVIDUAL_OUTPUT_DIRECTORY / f"{stock_code}_consolidation_analysis.csv"
    )

    data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def store_period_data(
    stock_code: str,
    periods: pd.DataFrame,
) -> Path:
    PERIOD_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = PERIOD_OUTPUT_DIRECTORY / f"{stock_code}_consolidation_periods.csv"

    periods.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def store_summary(
    stock_code: str,
    summary: pd.DataFrame,
) -> Path:
    SUMMARY_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = SUMMARY_OUTPUT_DIRECTORY / f"{stock_code}_consolidation_summary.csv"

    summary.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def process_all_stocks() -> None:
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_period_data: list[pd.DataFrame] = []

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

            data = load_activity_data(
                input_path=input_path,
                stock_code=stock_code,
            )

            data = calculate_box_features(data=data)

            data = identify_consolidation_days(data=data)

            data = assign_candidate_groups(data=data)

            fixed_box_periods = build_fixed_box_periods(data=data)

            data = mark_valid_consolidation_days(
                data=data,
                periods=(fixed_box_periods),
            )

            period_data = extract_consolidation_periods(
                data=data,
                periods=(fixed_box_periods),
                stock_code=stock_code,
            )

            summary_data = build_consolidation_summary(
                data=data,
                periods=period_data,
                stock_code=stock_code,
            )

            individual_path = store_individual_analysis(
                stock_code=stock_code,
                data=data,
            )

            period_path = store_period_data(
                stock_code=stock_code,
                periods=period_data,
            )

            summary_path = store_summary(
                stock_code=stock_code,
                summary=summary_data,
            )

            if not period_data.empty:
                all_period_data.append(period_data)

            all_summary_data.append(summary_data)

            processing_records.append(
                {
                    "stock_code": (stock_code),
                    "status": ("success"),
                    "rows": (len(data)),
                    "consolidation_periods": (len(period_data)),
                    "error_message": "",
                }
            )

            print(
                f"[SUCCESS] "
                f"Consolidation days: "
                f"{int(data['is_consolidation'].sum())}"
            )

            print(f"[SUCCESS] " f"Consolidation periods: " f"{len(period_data)}")

            if not period_data.empty:
                print(
                    f"[SUCCESS] "
                    f"Longest period: "
                    f"{int(period_data['duration_days'].max())} "
                    f"days"
                )

                print(
                    f"[SUCCESS] "
                    f"Maximum box range: "
                    f"{period_data['box_range'].max():.4f}"
                )

            print(f"[SAVED] " f"{individual_path}")

            print(f"[SAVED] " f"{period_path}")

            print(f"[SAVED] " f"{summary_path}")

        except Exception as error:
            processing_records.append(
                {
                    "stock_code": (stock_code),
                    "status": ("failed"),
                    "rows": 0,
                    "consolidation_periods": 0,
                    "error_message": (str(error)),
                }
            )

            print(f"[FAILED] " f"{stock_code}: " f"{error}")

    if all_period_data:
        combined_period_data = pd.concat(
            all_period_data,
            ignore_index=True,
        )

        combined_period_data = combined_period_data.sort_values(
            by=[
                "stock_code",
                "start_date",
            ]
        ).reset_index(drop=True)

        combined_period_data.to_csv(
            COMBINED_PERIOD_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"\n[SAVED] " f"Combined periods: " f"{COMBINED_PERIOD_OUTPUT_PATH}")

    if all_summary_data:
        combined_summary = pd.concat(
            all_summary_data,
            ignore_index=True,
        )

        combined_summary = combined_summary.sort_values(
            by="consolidation_day_rate",
            ascending=False,
        ).reset_index(drop=True)

        combined_summary.to_csv(
            COMBINED_SUMMARY_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"[SAVED] " f"Combined summary: " f"{COMBINED_SUMMARY_OUTPUT_PATH}")

        print("\n========== " "CONSOLIDATION SUMMARY " "==========")

        display_columns = [
            "stock_code",
            "consolidation_period_count",
            "consolidation_days",
            "consolidation_day_rate",
            "average_duration_days",
            "maximum_duration_days",
            "average_box_range",
            "active_consolidation_count",
            "moderate_consolidation_count",
            "mild_consolidation_count",
        ]

        print(combined_summary[display_columns].to_string(index=False))

    processing_summary = pd.DataFrame(processing_records)

    processing_summary.to_csv(
        PROCESSING_SUMMARY_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\n[SAVED] " f"Processing summary: " f"{PROCESSING_SUMMARY_OUTPUT_PATH}")

    success_count = int((processing_summary["status"] == "success").sum())

    failed_count = int((processing_summary["status"] == "failed").sum())

    print("\n========== " "PROCESSING RESULT " "==========")

    print(f"Total stocks: " f"{total_stocks}")

    print(f"Successful: " f"{success_count}")

    print(f"Failed: " f"{failed_count}")


if __name__ == "__main__":
    process_all_stocks()
