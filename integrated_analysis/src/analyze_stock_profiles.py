from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# Project configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MASTER_PATH = (
    PROJECT_ROOT
    / "integrated_analysis"
    / "data"
    / "master"
    / "a_share_analysis_master_2025.csv"
)

PROCESSED_DIRECTORY = PROJECT_ROOT / "integrated_analysis" / "data" / "processed"

TABLE_DIRECTORY = PROJECT_ROOT / "integrated_analysis" / "data" / "output" / "tables"

PROFILE_OUTPUT_PATH = PROCESSED_DIRECTORY / "stock_profiles_2025.csv"

INTEGRATED_TABLE_PATH = TABLE_DIRECTORY / "integrated_stock_profiles.csv"

FUNDAMENTAL_TABLE_PATH = TABLE_DIRECTORY / "fundamental_comparison.csv"

VALUATION_TABLE_PATH = TABLE_DIRECTORY / "valuation_comparison.csv"

ACTIVITY_TABLE_PATH = TABLE_DIRECTORY / "activity_comparison.csv"


# ============================================================
# Load master dataset
# ============================================================


def load_master_dataset() -> pd.DataFrame:
    print(f"[LOAD] Master dataset: " f"{MASTER_PATH}")

    if not MASTER_PATH.exists():
        raise FileNotFoundError(f"Master dataset not found: " f"{MASTER_PATH}")

    data = pd.read_csv(
        MASTER_PATH,
        encoding="utf-8-sig",
        dtype={
            "stock_code": str,
        },
    )

    data.columns = data.columns.astype(str).str.strip()

    data = data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    if data["stock_code"].duplicated().any():
        raise RuntimeError("Duplicate stock codes found " "in master dataset.")

    return data


# ============================================================
# Utility functions
# ============================================================


def percentile_rank(
    series: pd.Series,
    higher_is_better: bool = True,
) -> pd.Series:
    numeric_series = pd.to_numeric(
        series,
        errors="coerce",
    )

    if higher_is_better:
        return numeric_series.rank(
            pct=True,
            ascending=True,
        )

    return numeric_series.rank(
        pct=True,
        ascending=False,
    )


def average_available(
    data: pd.DataFrame,
    columns: list[str],
) -> pd.Series:
    existing_columns = [column for column in columns if column in data.columns]

    if not existing_columns:
        return pd.Series(
            np.nan,
            index=data.index,
        )

    return data[existing_columns].mean(
        axis=1,
        skipna=True,
    )


def classify_percentile(
    value: float,
    high_label: str,
    middle_label: str,
    low_label: str,
) -> str:
    if pd.isna(value):
        return "unavailable"

    if value >= 0.67:
        return high_label

    if value >= 0.33:
        return middle_label

    return low_label


# ============================================================
# Fundamental analysis
# ============================================================


def calculate_fundamental_scores(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    # Growth
    result["revenue_growth_rank"] = percentile_rank(result["revenue_yoy"])

    result["profit_growth_rank"] = percentile_rank(result["parent_net_profit_yoy"])

    result["asset_growth_rank"] = percentile_rank(result["total_assets_growth"])

    result["growth_score"] = average_available(
        data=result,
        columns=[
            "revenue_growth_rank",
            "profit_growth_rank",
            "asset_growth_rank",
        ],
    )

    # Profitability
    result["gross_margin_rank"] = percentile_rank(result["gross_margin"])

    result["net_margin_rank"] = percentile_rank(result["net_margin"])

    result["roe_rank"] = percentile_rank(result["roe"])

    result["profitability_score"] = average_available(
        data=result,
        columns=[
            "gross_margin_rank",
            "net_margin_rank",
            "roe_rank",
        ],
    )

    # Balance-sheet quality
    result["debt_quality_rank"] = percentile_rank(
        result["debt_to_asset_ratio"],
        higher_is_better=False,
    )

    result["current_ratio_rank"] = percentile_rank(result["current_ratio"])

    result["financial_strength_score"] = average_available(
        data=result,
        columns=[
            "debt_quality_rank",
            "current_ratio_rank",
        ],
    )

    result["fundamental_score"] = average_available(
        data=result,
        columns=[
            "growth_score",
            "profitability_score",
            "financial_strength_score",
        ],
    )

    result["growth_profile"] = result["growth_score"].map(
        lambda value: classify_percentile(
            value=value,
            high_label="strong_growth",
            middle_label="moderate_growth",
            low_label="weak_growth",
        )
    )

    result["profitability_profile"] = result["profitability_score"].map(
        lambda value: classify_percentile(
            value=value,
            high_label=("high_profitability"),
            middle_label=("moderate_profitability"),
            low_label=("low_profitability"),
        )
    )

    return result


# ============================================================
# Valuation analysis
# ============================================================


def calculate_valuation_scores(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    # Negative PE is economically different
    # from a low positive PE.
    result["valid_positive_pe"] = result["pe_ttm_median"].where(
        result["pe_ttm_median"] > 0
    )

    result["pe_value_rank"] = percentile_rank(
        result["valid_positive_pe"],
        higher_is_better=False,
    )

    result["pb_value_rank"] = percentile_rank(
        result["pb_median"],
        higher_is_better=False,
    )

    result["valuation_score"] = average_available(
        data=result,
        columns=[
            "pe_value_rank",
            "pb_value_rank",
        ],
    )

    def classify_valuation(
        row: pd.Series,
    ) -> str:
        pe = row["pe_ttm_median"]

        score = row["valuation_score"]

        if pd.isna(pe):
            return "unavailable"

        if pe <= 0:
            return "loss_making_pe"

        return classify_percentile(
            value=score,
            high_label="relatively_low_valuation",
            middle_label="mid_valuation",
            low_label="relatively_high_valuation",
        )

    result["valuation_profile"] = result.apply(
        classify_valuation,
        axis=1,
    )

    return result


# ============================================================
# Market activity analysis
# ============================================================


def calculate_activity_scores(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["volatility_rank"] = percentile_rank(result["annualized_volatility"])

    result["turnover_rank"] = percentile_rank(result["average_turnover"])

    result["large_move_rank"] = percentile_rank(result["large_move_rate"])

    result["volume_surge_rank"] = percentile_rank(result["volume_surge_rate"])

    result["activity_score"] = average_available(
        data=result,
        columns=[
            "volatility_rank",
            "turnover_rank",
            "large_move_rank",
            "volume_surge_rank",
        ],
    )

    result["relative_activity_profile"] = result["activity_score"].map(
        lambda value: classify_percentile(
            value=value,
            high_label=("high_activity"),
            middle_label=("moderate_activity"),
            low_label=("low_activity"),
        )
    )

    return result


# ============================================================
# Limit-event analysis
# ============================================================


def calculate_limit_event_scores(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["limit_up_rank"] = percentile_rank(result["limit_up_count"])

    result["failed_limit_rank"] = percentile_rank(result["failed_limit_up_rate"])

    result["consecutive_limit_rank"] = percentile_rank(
        result["maximum_consecutive_limit_up_days"]
    )

    result["limit_event_score"] = average_available(
        data=result,
        columns=[
            "limit_up_rank",
            "consecutive_limit_rank",
        ],
    )

    result["limit_event_profile"] = result["limit_event_score"].map(
        lambda value: classify_percentile(
            value=value,
            high_label=("strong_limit_activity"),
            middle_label=("moderate_limit_activity"),
            low_label=("low_limit_activity"),
        )
    )

    return result


# ============================================================
# Consolidation analysis
# ============================================================


def calculate_consolidation_scores(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["consolidation_rank"] = percentile_rank(result["consolidation_day_rate"])

    result["duration_rank"] = percentile_rank(result["average_duration_days"])

    result["consolidation_score"] = average_available(
        data=result,
        columns=[
            "consolidation_rank",
            "duration_rank",
        ],
    )

    result["consolidation_profile"] = result["consolidation_score"].map(
        lambda value: classify_percentile(
            value=value,
            high_label=("consolidation_dominant"),
            middle_label=("mixed_structure"),
            low_label=("trend_dominant"),
        )
    )

    return result


# ============================================================
# Integrated market style
# ============================================================


def classify_market_style(
    row: pd.Series,
) -> str:
    activity = row["activity_score"]
    consolidation = row["consolidation_score"]

    if pd.isna(activity) or pd.isna(consolidation):
        return "unavailable"

    if activity >= 0.67:
        activity_level = "high"

    elif activity >= 0.33:
        activity_level = "moderate"

    else:
        activity_level = "low"

    if consolidation >= 0.67:
        structure = "consolidation"

    elif consolidation >= 0.33:
        structure = "mixed"

    else:
        structure = "trend"

    style_map = {
        ("high", "trend"): "active_trending",
        ("high", "mixed"): "active_mixed",
        ("high", "consolidation"): "active_consolidating",
        ("moderate", "trend"): "moderate_trending",
        ("moderate", "mixed"): "balanced",
        ("moderate", "consolidation"): "moderate_consolidating",
        ("low", "trend"): "quiet_trending",
        ("low", "mixed"): "quiet_mixed",
        ("low", "consolidation"): "quiet_consolidating",
    }

    return style_map[
        (
            activity_level,
            structure,
        )
    ]


# ============================================================
# Build profiles
# ============================================================


def build_stock_profiles(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = calculate_fundamental_scores(data=data)

    result = calculate_valuation_scores(data=result)

    result = calculate_activity_scores(data=result)

    result = calculate_limit_event_scores(data=result)

    result = calculate_consolidation_scores(data=result)

    result["market_style"] = result.apply(
        classify_market_style,
        axis=1,
    )

    return result


# ============================================================
# Output tables
# ============================================================


def build_fundamental_table(
    data: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "stock_code",
        "stock_name",
        "revenue_yoy",
        "parent_net_profit_yoy",
        "gross_margin",
        "net_margin",
        "roe",
        "debt_to_asset_ratio",
        "current_ratio",
        "growth_score",
        "profitability_score",
        "financial_strength_score",
        "fundamental_score",
        "growth_profile",
        "profitability_profile",
    ]

    return data[columns].sort_values(
        by="fundamental_score",
        ascending=False,
    )


def build_valuation_table(
    data: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "stock_code",
        "stock_name",
        "pe_ttm_median",
        "pb_median",
        "total_market_value_year_end",
        "pe_ttm_nonpositive_day_rate",
        "valuation_score",
        "valuation_profile",
    ]

    return data[columns].sort_values(
        by="valuation_score",
        ascending=False,
        na_position="last",
    )


def build_activity_table(
    data: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "stock_code",
        "stock_name",
        "annualized_volatility",
        "average_turnover",
        "large_move_rate",
        "volume_surge_rate",
        "activity_score",
        "activity_style",
        "relative_activity_profile",
        "limit_up_count",
        "failed_limit_up_rate",
        "maximum_consecutive_limit_up_days",
        "consolidation_day_rate",
        "market_style",
    ]

    return data[columns].sort_values(
        by="activity_score",
        ascending=False,
    )


def build_integrated_table(
    data: pd.DataFrame,
) -> pd.DataFrame:
    columns = [
        "stock_code",
        "stock_name",
        "fundamental_score",
        "growth_profile",
        "profitability_profile",
        "valuation_score",
        "valuation_profile",
        "activity_score",
        "relative_activity_profile",
        "limit_event_score",
        "limit_event_profile",
        "consolidation_score",
        "consolidation_profile",
        "market_style",
    ]

    return data[columns].sort_values(
        by=[
            "fundamental_score",
            "activity_score",
        ],
        ascending=[
            False,
            False,
        ],
    )


# ============================================================
# Main
# ============================================================


def main() -> None:
    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    TABLE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n========== " "INTEGRATED STOCK PROFILE ANALYSIS " "==========")

    master_data = load_master_dataset()

    profile_data = build_stock_profiles(data=master_data)

    profile_data.to_csv(
        PROFILE_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    fundamental_table = build_fundamental_table(data=profile_data)

    valuation_table = build_valuation_table(data=profile_data)

    activity_table = build_activity_table(data=profile_data)

    integrated_table = build_integrated_table(data=profile_data)

    fundamental_table.to_csv(
        FUNDAMENTAL_TABLE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    valuation_table.to_csv(
        VALUATION_TABLE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    activity_table.to_csv(
        ACTIVITY_TABLE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    integrated_table.to_csv(
        INTEGRATED_TABLE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Profiles: " f"{PROFILE_OUTPUT_PATH}")

    print(f"[SAVED] Fundamental table: " f"{FUNDAMENTAL_TABLE_PATH}")

    print(f"[SAVED] Valuation table: " f"{VALUATION_TABLE_PATH}")

    print(f"[SAVED] Activity table: " f"{ACTIVITY_TABLE_PATH}")

    print(f"[SAVED] Integrated table: " f"{INTEGRATED_TABLE_PATH}")

    print("\n========== " "INTEGRATED PROFILE SUMMARY " "==========")

    display_columns = [
        "stock_code",
        "stock_name",
        "fundamental_score",
        "valuation_profile",
        "activity_score",
        "limit_event_profile",
        "consolidation_profile",
        "market_style",
    ]

    print(
        integrated_table[
            [column for column in display_columns if column in integrated_table.columns]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
