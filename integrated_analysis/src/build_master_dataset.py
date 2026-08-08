from pathlib import Path
import re

import numpy as np
import pandas as pd

# ============================================================
# Project configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INTEGRATED_ANALYSIS_ROOT = PROJECT_ROOT / "integrated_analysis"

ANALYSIS_YEAR = 2025


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


NUMERIC_TO_FULL_CODE = {stock_code[-6:]: stock_code for stock_code in A_STOCK_CODES}


# ============================================================
# Source paths
# ============================================================

FUNDAMENTAL_PATH = (
    PROJECT_ROOT
    / "fundamentals"
    / "data"
    / "factors"
    / "a_share"
    / "a_share_fundamental_factors.csv"
)

VALUATION_PATH = (
    PROJECT_ROOT
    / "market_data_pipeline"
    / "data"
    / "cleaned"
    / "valuation"
    / "a_share_valuation.csv"
)

INDICATOR_DIRECTORY = PROJECT_ROOT / "market_data_pipeline" / "data" / "indicators"

ACTIVITY_PATH = (
    PROJECT_ROOT
    / "market_data_pipeline"
    / "data"
    / "analysis"
    / "activity_analysis"
    / "combined_activity_summary.csv"
)

LIMIT_PATH = (
    PROJECT_ROOT
    / "market_data_pipeline"
    / "data"
    / "analysis"
    / "limit_analysis"
    / "combined_limit_summary.csv"
)

CONSOLIDATION_PATH = (
    PROJECT_ROOT
    / "market_data_pipeline"
    / "data"
    / "analysis"
    / "consolidation_analysis"
    / "combined_consolidation_summary.csv"
)


# ============================================================
# Output paths
# ============================================================

PROCESSED_DIRECTORY = INTEGRATED_ANALYSIS_ROOT / "data" / "processed"

MASTER_DIRECTORY = INTEGRATED_ANALYSIS_ROOT / "data" / "master"

FUNDAMENTAL_SUMMARY_OUTPUT_PATH = PROCESSED_DIRECTORY / "fundamental_summary_2025.csv"

VALUATION_SUMMARY_OUTPUT_PATH = PROCESSED_DIRECTORY / "valuation_summary_2025.csv"

VALIDATION_OUTPUT_PATH = PROCESSED_DIRECTORY / "master_build_validation.csv"

MASTER_OUTPUT_PATH = MASTER_DIRECTORY / "a_share_analysis_master_2025.csv"


# ============================================================
# Stock code normalization
# ============================================================


def normalize_stock_code(
    value,
) -> str:
    if pd.isna(value):
        raise ValueError("Stock code cannot be missing.")

    text = str(value).strip().lower()

    # Handle values such as:
    # 100
    # 100.0
    # 000100
    # sz000100
    # sh600231

    if re.fullmatch(
        r"\d+\.0+",
        text,
    ):
        text = str(int(float(text)))

    match = re.search(
        r"(\d{1,6})$",
        text,
    )

    if match is None:
        raise ValueError(f"Cannot parse stock code: {value}")

    numeric_code = match.group(1).zfill(6)

    if numeric_code not in NUMERIC_TO_FULL_CODE:
        raise ValueError(
            f"Stock code {numeric_code} " f"is not in the target universe."
        )

    return NUMERIC_TO_FULL_CODE[numeric_code]


def normalize_stock_code_column(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    if "stock_code" not in result.columns:
        raise KeyError("Missing required column: " "'stock_code'.")

    result["stock_code"] = result["stock_code"].map(normalize_stock_code)

    return result


# ============================================================
# Fundamental data
# ============================================================


def load_fundamental_data() -> pd.DataFrame:
    print(f"[LOAD] Fundamental data: " f"{FUNDAMENTAL_PATH}")

    data = pd.read_csv(
        FUNDAMENTAL_PATH,
        encoding="utf-8-sig",
        dtype={
            "stock_code": str,
        },
    )

    data.columns = data.columns.astype(str).str.strip()

    data = normalize_stock_code_column(data=data)

    data["report_date"] = pd.to_datetime(
        data["report_date"],
        errors="coerce",
    )

    data["notice_date"] = pd.to_datetime(
        data["notice_date"],
        errors="coerce",
    )

    return data


def build_fundamental_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result = result[result["report_date"].dt.year == ANALYSIS_YEAR].copy()

    if result.empty:
        raise RuntimeError(f"No fundamental records found " f"for {ANALYSIS_YEAR}.")

    # If several records exist for the same
    # reporting date, prefer the latest
    # notice date.
    result = result.sort_values(
        by=[
            "stock_code",
            "report_date",
            "notice_date",
        ],
        na_position="first",
    )

    result = result.drop_duplicates(
        subset=["stock_code"],
        keep="last",
    ).reset_index(drop=True)

    selected_columns = [
        "stock_code",
        "stock_name",
        "report_date",
        "notice_date",
        "report_type",
        "currency",
        "revenue",
        "revenue_yoy",
        "parent_net_profit",
        "parent_net_profit_yoy",
        "net_profit",
        "gross_margin",
        "net_margin",
        "total_assets",
        "total_assets_growth",
        "total_liabilities",
        "debt_to_asset_ratio",
        "current_ratio",
        "parent_equity",
        "roe",
        "operating_cash_flow",
        "operating_cash_flow_to_net_profit",
    ]

    existing_columns = [
        column for column in selected_columns if column in result.columns
    ]

    result = result[existing_columns].copy()

    result = result.rename(
        columns={
            "report_date": "fundamental_report_date",
            "notice_date": "fundamental_notice_date",
            "report_type": "fundamental_report_type",
            "currency": "fundamental_currency",
        }
    )

    result["has_fundamental_data"] = True

    return result


# ============================================================
# Trading dates
# ============================================================


def get_indicator_path(
    stock_code: str,
) -> Path:
    path = INDICATOR_DIRECTORY / (f"cleaned_{stock_code}" f"_with_ma_columns.csv")

    if not path.exists():
        raise FileNotFoundError(
            f"Indicator file not found for " f"{stock_code}: {path}"
        )

    return path


def load_trading_dates(
    stock_code: str,
) -> pd.DatetimeIndex:
    path = get_indicator_path(stock_code=stock_code)

    data = pd.read_csv(
        path,
        encoding="utf-8-sig",
        usecols=lambda column: (str(column).strip().lower() == "date"),
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    if "date" not in data.columns:
        raise KeyError(f"'date' column not found " f"in {path}.")

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce",
    )

    dates = data["date"].dropna()

    dates = dates[dates.dt.year == ANALYSIS_YEAR]

    return pd.DatetimeIndex(dates.unique())


# ============================================================
# Valuation data
# ============================================================


def load_valuation_data() -> pd.DataFrame:
    print(f"[LOAD] Valuation data: " f"{VALUATION_PATH}")

    data = pd.read_csv(
        VALUATION_PATH,
        encoding="utf-8-sig",
        dtype={
            "stock_code": str,
        },
    )

    data.columns = data.columns.astype(str).str.strip().str.lower()

    data = normalize_stock_code_column(data=data)

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce",
    )

    numeric_columns = [
        "pe_ttm",
        "pe_static",
        "pb",
        "total_market_value",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    data = data.dropna(
        subset=[
            "stock_code",
            "date",
        ]
    )

    data = data.drop_duplicates(
        subset=[
            "stock_code",
            "date",
        ],
        keep="last",
    )

    return data


def safe_mean(
    series: pd.Series,
) -> float:
    valid = series.dropna()

    if valid.empty:
        return float("nan")

    return float(valid.mean())


def safe_median(
    series: pd.Series,
) -> float:
    valid = series.dropna()

    if valid.empty:
        return float("nan")

    return float(valid.median())


def safe_min(
    series: pd.Series,
) -> float:
    valid = series.dropna()

    if valid.empty:
        return float("nan")

    return float(valid.min())


def safe_max(
    series: pd.Series,
) -> float:
    valid = series.dropna()

    if valid.empty:
        return float("nan")

    return float(valid.max())


def build_valuation_summary(
    data: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict] = []

    for stock_code in A_STOCK_CODES:
        stock_data = data[data["stock_code"] == stock_code].copy()

        stock_data = stock_data[stock_data["date"].dt.year == ANALYSIS_YEAR].copy()

        trading_dates = load_trading_dates(stock_code=stock_code)

        # Remove weekends / non-trading
        # natural-day observations.
        stock_data = stock_data[stock_data["date"].isin(trading_dates)].copy()

        stock_data = stock_data.sort_values(by="date").reset_index(drop=True)

        if stock_data.empty:
            print(
                f"[WARNING] No valuation data "
                f"after trading-date filtering "
                f"for {stock_code}."
            )

            records.append(
                {
                    "stock_code": stock_code,
                    "has_valuation_data": False,
                }
            )

            continue

        year_end_row = stock_data.iloc[-1]

        pe_ttm_positive = stock_data.loc[
            stock_data["pe_ttm"] > 0,
            "pe_ttm",
        ]

        pe_static_positive = stock_data.loc[
            stock_data["pe_static"] > 0,
            "pe_static",
        ]

        valid_pe_ttm = stock_data["pe_ttm"].dropna()

        nonpositive_pe_ttm_rate = (
            (valid_pe_ttm <= 0).mean() if not valid_pe_ttm.empty else float("nan")
        )

        record = {
            "stock_code": stock_code,
            "valuation_start_date": stock_data["date"].min(),
            "valuation_end_date": stock_data["date"].max(),
            "valuation_trading_days": len(stock_data),
            # PE TTM
            "pe_ttm_mean": safe_mean(stock_data["pe_ttm"]),
            "pe_ttm_median": safe_median(stock_data["pe_ttm"]),
            "pe_ttm_min": safe_min(stock_data["pe_ttm"]),
            "pe_ttm_max": safe_max(stock_data["pe_ttm"]),
            "pe_ttm_year_end": year_end_row["pe_ttm"],
            "pe_ttm_positive_mean": safe_mean(pe_ttm_positive),
            "pe_ttm_positive_median": safe_median(pe_ttm_positive),
            "pe_ttm_nonpositive_day_rate": nonpositive_pe_ttm_rate,
            # Static PE
            "pe_static_mean": safe_mean(stock_data["pe_static"]),
            "pe_static_median": safe_median(stock_data["pe_static"]),
            "pe_static_year_end": year_end_row["pe_static"],
            "pe_static_positive_mean": safe_mean(pe_static_positive),
            # PB
            "pb_mean": safe_mean(stock_data["pb"]),
            "pb_median": safe_median(stock_data["pb"]),
            "pb_min": safe_min(stock_data["pb"]),
            "pb_max": safe_max(stock_data["pb"]),
            "pb_year_end": year_end_row["pb"],
            # Market value
            "total_market_value_mean": safe_mean(stock_data["total_market_value"]),
            "total_market_value_median": safe_median(stock_data["total_market_value"]),
            "total_market_value_year_end": year_end_row["total_market_value"],
            "has_valuation_data": True,
        }

        records.append(record)

    return pd.DataFrame(records)


# ============================================================
# Existing summary files
# ============================================================


def load_summary_source(
    path: Path,
    source_name: str,
) -> pd.DataFrame:
    print(f"[LOAD] {source_name}: " f"{path}")

    if not path.exists():
        raise FileNotFoundError(f"{source_name} source " f"not found: {path}")

    data = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={
            "stock_code": str,
        },
    )

    data.columns = data.columns.astype(str).str.strip()

    data = normalize_stock_code_column(data=data)

    data = data[data["stock_code"].isin(A_STOCK_CODES)].copy()

    duplicate_mask = data["stock_code"].duplicated(keep=False)

    if duplicate_mask.any():
        duplicate_codes = (
            data.loc[
                duplicate_mask,
                "stock_code",
            ]
            .unique()
            .tolist()
        )

        raise RuntimeError(
            f"{source_name} contains " f"duplicate stock rows: " f"{duplicate_codes}"
        )

    # These metadata columns are
    # already represented elsewhere
    # and would cause merge collisions.
    metadata_columns = [
        "start_date",
        "end_date",
        "trading_days",
    ]

    removable_columns = [
        column for column in metadata_columns if column in data.columns
    ]

    data = data.drop(columns=removable_columns)

    availability_column = f"has_{source_name}_data"

    data[availability_column] = True

    return data


# ============================================================
# Validation
# ============================================================


def build_validation_record(
    source_name: str,
    data: pd.DataFrame,
) -> dict:
    expected_codes = set(A_STOCK_CODES)

    actual_codes = set(data["stock_code"].dropna().tolist())

    missing_codes = sorted(expected_codes - actual_codes)

    extra_codes = sorted(actual_codes - expected_codes)

    duplicate_codes = (
        data.loc[
            data["stock_code"].duplicated(keep=False),
            "stock_code",
        ]
        .unique()
        .tolist()
    )

    return {
        "source": source_name,
        "rows": len(data),
        "unique_stocks": data["stock_code"].nunique(),
        "missing_stock_count": len(missing_codes),
        "missing_stocks": " | ".join(missing_codes),
        "extra_stock_count": len(extra_codes),
        "extra_stocks": " | ".join(extra_codes),
        "duplicate_stock_count": len(duplicate_codes),
        "duplicate_stocks": " | ".join(sorted(duplicate_codes)),
    }


def validate_no_column_overlap(
    left: pd.DataFrame,
    right: pd.DataFrame,
    source_name: str,
) -> None:
    overlap = set(left.columns) & set(right.columns)

    overlap.discard("stock_code")

    if overlap:
        raise RuntimeError(
            f"Column collision while merging " f"{source_name}: " f"{sorted(overlap)}"
        )


def merge_source(
    master: pd.DataFrame,
    source: pd.DataFrame,
    source_name: str,
) -> pd.DataFrame:
    validate_no_column_overlap(
        left=master,
        right=source,
        source_name=source_name,
    )

    result = master.merge(
        source,
        on="stock_code",
        how="left",
        validate="one_to_one",
    )

    return result


# ============================================================
# Master dataset
# ============================================================


def build_master_dataset(
    fundamental_summary: pd.DataFrame,
    valuation_summary: pd.DataFrame,
    activity_summary: pd.DataFrame,
    limit_summary: pd.DataFrame,
    consolidation_summary: pd.DataFrame,
) -> pd.DataFrame:
    master = pd.DataFrame({"stock_code": A_STOCK_CODES})

    sources = [
        (
            "fundamental",
            fundamental_summary,
        ),
        (
            "valuation",
            valuation_summary,
        ),
        (
            "activity",
            activity_summary,
        ),
        (
            "limit",
            limit_summary,
        ),
        (
            "consolidation",
            consolidation_summary,
        ),
    ]

    for source_name, source_data in sources:
        print(f"[MERGE] {source_name}")

        master = merge_source(
            master=master,
            source=source_data,
            source_name=source_name,
        )

    availability_columns = [
        "has_fundamental_data",
        "has_valuation_data",
        "has_activity_data",
        "has_limit_data",
        "has_consolidation_data",
    ]

    for column in availability_columns:
        if column not in master.columns:
            master[column] = False

        master[column] = master[column].fillna(False).astype(bool)

    master["data_complete"] = master[availability_columns].all(axis=1)

    # Put identity and availability
    # fields at the front.
    front_columns = [
        "stock_code",
        "stock_name",
        "fundamental_report_date",
        "fundamental_notice_date",
        "fundamental_report_type",
        "fundamental_currency",
        "has_fundamental_data",
        "has_valuation_data",
        "has_activity_data",
        "has_limit_data",
        "has_consolidation_data",
        "data_complete",
    ]

    existing_front_columns = [
        column for column in front_columns if column in master.columns
    ]

    remaining_columns = [
        column for column in master.columns if column not in existing_front_columns
    ]

    master = master[existing_front_columns + remaining_columns]

    return master


# ============================================================
# Final checks
# ============================================================


def validate_master_dataset(
    master: pd.DataFrame,
) -> None:
    expected_count = len(A_STOCK_CODES)

    if len(master) != expected_count:
        raise RuntimeError(
            f"Master dataset has " f"{len(master)} rows, " f"expected {expected_count}."
        )

    if master["stock_code"].duplicated().any():
        raise RuntimeError("Duplicate stock codes found " "in master dataset.")

    actual_codes = set(master["stock_code"])

    expected_codes = set(A_STOCK_CODES)

    if actual_codes != expected_codes:
        missing = sorted(expected_codes - actual_codes)

        extra = sorted(actual_codes - expected_codes)

        raise RuntimeError(
            f"Master universe mismatch. " f"Missing: {missing}. " f"Extra: {extra}."
        )


# ============================================================
# Main
# ============================================================


def main() -> None:
    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    MASTER_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n========== " "BUILD MASTER DATASET " "==========")

    # --------------------------------------------------------
    # Fundamentals
    # --------------------------------------------------------

    fundamental_data = load_fundamental_data()

    fundamental_summary = build_fundamental_summary(data=fundamental_data)

    fundamental_summary.to_csv(
        FUNDAMENTAL_SUMMARY_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Fundamental summary: " f"{FUNDAMENTAL_SUMMARY_OUTPUT_PATH}")

    # --------------------------------------------------------
    # Valuation
    # --------------------------------------------------------

    valuation_data = load_valuation_data()

    valuation_summary = build_valuation_summary(data=valuation_data)

    valuation_summary.to_csv(
        VALUATION_SUMMARY_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Valuation summary: " f"{VALUATION_SUMMARY_OUTPUT_PATH}")

    # --------------------------------------------------------
    # Existing analysis summaries
    # --------------------------------------------------------

    activity_summary = load_summary_source(
        path=ACTIVITY_PATH,
        source_name="activity",
    )

    limit_summary = load_summary_source(
        path=LIMIT_PATH,
        source_name="limit",
    )

    consolidation_summary = load_summary_source(
        path=CONSOLIDATION_PATH,
        source_name="consolidation",
    )

    # --------------------------------------------------------
    # Validation report
    # --------------------------------------------------------

    validation_records = [
        build_validation_record(
            source_name="fundamental",
            data=fundamental_summary,
        ),
        build_validation_record(
            source_name="valuation",
            data=valuation_summary,
        ),
        build_validation_record(
            source_name="activity",
            data=activity_summary,
        ),
        build_validation_record(
            source_name="limit",
            data=limit_summary,
        ),
        build_validation_record(
            source_name="consolidation",
            data=consolidation_summary,
        ),
    ]

    validation_data = pd.DataFrame(validation_records)

    validation_data.to_csv(
        VALIDATION_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n========== " "SOURCE VALIDATION " "==========")

    print(validation_data.to_string(index=False))

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    master = build_master_dataset(
        fundamental_summary=(fundamental_summary),
        valuation_summary=(valuation_summary),
        activity_summary=(activity_summary),
        limit_summary=(limit_summary),
        consolidation_summary=(consolidation_summary),
    )

    validate_master_dataset(master=master)

    master.to_csv(
        MASTER_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    complete_count = int(master["data_complete"].sum())

    incomplete_count = len(master) - complete_count

    print("\n========== " "MASTER DATASET RESULT " "==========")

    print(f"Rows: " f"{len(master)}")

    print(f"Columns: " f"{len(master.columns)}")

    print(f"Complete stocks: " f"{complete_count}")

    print(f"Incomplete stocks: " f"{incomplete_count}")

    print(f"\n[SAVED] Master dataset: " f"{MASTER_OUTPUT_PATH}")

    preview_columns = [
        "stock_code",
        "stock_name",
        "revenue_yoy",
        "parent_net_profit_yoy",
        "roe",
        "debt_to_asset_ratio",
        "pe_ttm_median",
        "pb_median",
        "annualized_volatility",
        "average_turnover",
        "activity_style",
        "limit_up_count",
        "failed_limit_up_rate",
        "maximum_consecutive_limit_up_days",
        "consolidation_day_rate",
        "consolidation_period_count",
        "data_complete",
    ]

    existing_preview_columns = [
        column for column in preview_columns if column in master.columns
    ]

    print("\n========== " "MASTER PREVIEW " "==========")

    print(master[existing_preview_columns].to_string(index=False))


if __name__ == "__main__":
    main()
