from pathlib import Path
import time

import akshare as ak
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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


VALUATION_INDICATORS = {
    "pe_ttm": "市盈率(TTM)",
    "pe_static": "市盈率(静)",
    "pb": "市净率",
    "total_market_value": "总市值",
}


VALUATION_PERIOD = "近三年"

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"


RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw" / "valuation"

CLEANED_INDIVIDUAL_DIRECTORY = (
    PROJECT_ROOT / "data" / "cleaned" / "valuation" / "individual"
)

COMBINED_OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "cleaned" / "valuation" / "a_share_valuation.csv"
)

SUMMARY_OUTPUT_PATH = PROJECT_ROOT / "data" / "summary" / "valuation_fetch_summary.csv"


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
            f"Invalid A-share stock code: "
            f"{stock_code}. Expected formats such as "
            f"'sz002067' or 'sh600763'."
        )

    return normalized_code


def get_numeric_stock_code(
    stock_code: str,
) -> str:
    normalized_code = normalize_stock_code(stock_code)

    return normalized_code[2:]


def fetch_valuation_indicator(
    stock_code: str,
    indicator: str,
    period: str = VALUATION_PERIOD,
    max_retries: int = 3,
) -> pd.DataFrame:
    numeric_stock_code = get_numeric_stock_code(stock_code)

    for attempt in range(
        1,
        max_retries + 1,
    ):
        try:
            valuation_data: pd.DataFrame = ak.stock_zh_valuation_baidu(
                symbol=numeric_stock_code,
                indicator=indicator,
                period=period,
            )

            if valuation_data.empty:
                raise RuntimeError(
                    f"No valuation data returned for "
                    f"{stock_code}, indicator={indicator}."
                )

            return valuation_data

        except Exception as error:
            print(
                f"[RETRY {attempt}/{max_retries}] "
                f"{stock_code} "
                f"{indicator}: {error}"
            )

            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to fetch valuation data "
                    f"for {stock_code}, "
                    f"indicator={indicator}."
                ) from error

            time.sleep(3)

    raise RuntimeError(
        f"Unexpected valuation fetch failure: " f"{stock_code}, {indicator}."
    )


def validate_valuation_columns(
    data: pd.DataFrame,
) -> None:
    required_columns = [
        "date",
        "value",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing valuation columns: "
            f"{missing_columns}. "
            f"Available columns: "
            f"{data.columns.tolist()}"
        )


def clean_valuation_indicator(
    data: pd.DataFrame,
    stock_code: str,
    factor_name: str,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> pd.DataFrame:
    cleaned_data = data.copy()

    cleaned_data.columns = cleaned_data.columns.astype(str).str.strip()

    validate_valuation_columns(data=cleaned_data)

    cleaned_data["date"] = pd.to_datetime(
        cleaned_data["date"],
        errors="coerce",
    )

    cleaned_data["value"] = pd.to_numeric(
        cleaned_data["value"],
        errors="coerce",
    )

    cleaned_data = cleaned_data.dropna(
        subset=[
            "date",
            "value",
        ]
    )

    cleaned_data = cleaned_data[
        cleaned_data["date"].between(
            start_date,
            end_date,
        )
    ].copy()

    cleaned_data = cleaned_data.rename(
        columns={
            "value": factor_name,
        }
    )

    cleaned_data["stock_code"] = normalize_stock_code(stock_code)

    cleaned_data = cleaned_data[
        [
            "stock_code",
            "date",
            factor_name,
        ]
    ]

    cleaned_data = cleaned_data.drop_duplicates(
        subset=[
            "stock_code",
            "date",
        ],
        keep="last",
    )

    cleaned_data = cleaned_data.sort_values(by="date").reset_index(drop=True)

    return cleaned_data


def build_raw_output_path(
    stock_code: str,
    factor_name: str,
) -> Path:
    normalized_code = normalize_stock_code(stock_code)

    return (
        RAW_DIRECTORY
        / normalized_code
        / (f"{normalized_code}_" f"{factor_name}_" f"{VALUATION_PERIOD}.csv")
    )


def store_raw_valuation_data(
    stock_code: str,
    factor_name: str,
    raw_data: pd.DataFrame,
) -> Path:
    output_path = build_raw_output_path(
        stock_code=stock_code,
        factor_name=factor_name,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def merge_valuation_indicators(
    valuation_data_list: list[pd.DataFrame],
) -> pd.DataFrame:
    if not valuation_data_list:
        return pd.DataFrame()

    merged_data = valuation_data_list[0].copy()

    for valuation_data in valuation_data_list[1:]:
        merged_data = merged_data.merge(
            valuation_data,
            on=[
                "stock_code",
                "date",
            ],
            how="outer",
            validate="one_to_one",
        )

    merged_data = merged_data.sort_values(
        by=[
            "stock_code",
            "date",
        ]
    ).reset_index(drop=True)

    return merged_data


def inspect_calendar_coverage(
    data: pd.DataFrame,
) -> dict:
    if data.empty:
        return {
            "rows": 0,
            "earliest_date": pd.NaT,
            "latest_date": pd.NaT,
            "weekend_rows": 0,
            "weekday_rows": 0,
        }

    weekend_mask = data["date"].dt.dayofweek >= 5

    return {
        "rows": len(data),
        "earliest_date": (data["date"].min()),
        "latest_date": (data["date"].max()),
        "weekend_rows": int(weekend_mask.sum()),
        "weekday_rows": int((~weekend_mask).sum()),
    }


def build_indicator_summary(
    stock_code: str,
    factor_name: str,
    indicator_name: str,
    cleaned_data: pd.DataFrame,
    status: str,
    error_message: str = "",
) -> dict:
    coverage = inspect_calendar_coverage(data=cleaned_data)

    factor_missing_values = 0

    if not cleaned_data.empty and factor_name in cleaned_data.columns:
        factor_missing_values = int(cleaned_data[factor_name].isna().sum())

    return {
        "stock_code": normalize_stock_code(stock_code),
        "factor_name": factor_name,
        "indicator_name": indicator_name,
        "status": status,
        "rows": coverage["rows"],
        "earliest_date": (coverage["earliest_date"]),
        "latest_date": (coverage["latest_date"]),
        "weekday_rows": (coverage["weekday_rows"]),
        "weekend_rows": (coverage["weekend_rows"]),
        "missing_values": (factor_missing_values),
        "error_message": error_message,
    }


def store_stock_valuation_data(
    stock_code: str,
    valuation_data: pd.DataFrame,
) -> Path:
    normalized_code = normalize_stock_code(stock_code)

    CLEANED_INDIVIDUAL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CLEANED_INDIVIDUAL_DIRECTORY / (
        f"{normalized_code}_" f"valuation_" f"{START_DATE[:4]}.csv"
    )

    valuation_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def process_stock_valuation(
    stock_code: str,
) -> tuple[
    pd.DataFrame,
    list[dict],
]:
    normalized_code = normalize_stock_code(stock_code)

    print(f"\n[START] Valuation data: " f"{normalized_code}")

    cleaned_indicator_data: list[pd.DataFrame] = []

    indicator_summaries: list[dict] = []

    for (
        factor_name,
        indicator_name,
    ) in VALUATION_INDICATORS.items():
        try:
            raw_data = fetch_valuation_indicator(
                stock_code=normalized_code,
                indicator=indicator_name,
            )

            raw_path = store_raw_valuation_data(
                stock_code=normalized_code,
                factor_name=factor_name,
                raw_data=raw_data,
            )

            cleaned_data = clean_valuation_indicator(
                data=raw_data,
                stock_code=normalized_code,
                factor_name=factor_name,
            )

            if cleaned_data.empty:
                raise RuntimeError(
                    f"No data remained after filtering " f"{START_DATE} to {END_DATE}."
                )

            cleaned_indicator_data.append(cleaned_data)

            indicator_summaries.append(
                build_indicator_summary(
                    stock_code=normalized_code,
                    factor_name=factor_name,
                    indicator_name=indicator_name,
                    cleaned_data=cleaned_data,
                    status="success",
                )
            )

            print(
                f"[SUCCESS] {normalized_code} "
                f"{indicator_name}: "
                f"{len(cleaned_data)} rows"
            )

            print(f"          Raw: " f"{raw_path}")

        except Exception as error:
            indicator_summaries.append(
                build_indicator_summary(
                    stock_code=normalized_code,
                    factor_name=factor_name,
                    indicator_name=indicator_name,
                    cleaned_data=pd.DataFrame(),
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED] {normalized_code} " f"{indicator_name}: {error}")

        time.sleep(1)

    if not cleaned_indicator_data:
        raise RuntimeError(
            f"All valuation indicators failed for " f"{normalized_code}."
        )

    merged_data = merge_valuation_indicators(
        valuation_data_list=(cleaned_indicator_data)
    )

    output_path = store_stock_valuation_data(
        stock_code=normalized_code,
        valuation_data=merged_data,
    )

    print(f"[SAVED] {normalized_code}: " f"{output_path}")

    return (
        merged_data,
        indicator_summaries,
    )


def build_stock_summary(
    stock_code: str,
    data: pd.DataFrame,
    status: str,
    error_message: str = "",
) -> dict:
    normalized_code = normalize_stock_code(stock_code)

    if data.empty:
        return {
            "stock_code": normalized_code,
            "status": status,
            "rows": 0,
            "earliest_date": pd.NaT,
            "latest_date": pd.NaT,
            "missing_pe_ttm": 0,
            "missing_pe_static": 0,
            "missing_pb": 0,
            "missing_total_market_value": 0,
            "error_message": error_message,
        }

    summary = {
        "stock_code": normalized_code,
        "status": status,
        "rows": len(data),
        "earliest_date": (data["date"].min()),
        "latest_date": (data["date"].max()),
        "error_message": error_message,
    }

    for factor_name in VALUATION_INDICATORS:
        missing_column_name = f"missing_{factor_name}"

        if factor_name in data.columns:
            summary[missing_column_name] = int(data[factor_name].isna().sum())
        else:
            summary[missing_column_name] = len(data)

    return summary


def process_all_stock_valuations() -> None:
    all_valuation_data: list[pd.DataFrame] = []

    stock_summary_records: list[dict] = []

    indicator_summary_records: list[dict] = []

    for stock_code in A_STOCK_CODES:
        try:
            (
                stock_valuation_data,
                indicator_summaries,
            ) = process_stock_valuation(stock_code=stock_code)

            all_valuation_data.append(stock_valuation_data)

            indicator_summary_records.extend(indicator_summaries)

            stock_summary_records.append(
                build_stock_summary(
                    stock_code=stock_code,
                    data=stock_valuation_data,
                    status="success",
                )
            )

        except Exception as error:
            stock_summary_records.append(
                build_stock_summary(
                    stock_code=stock_code,
                    data=pd.DataFrame(),
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED STOCK] " f"{stock_code}: {error}")

    if all_valuation_data:
        combined_data = pd.concat(
            all_valuation_data,
            ignore_index=True,
        )

        combined_data = (
            combined_data.drop_duplicates(
                subset=[
                    "stock_code",
                    "date",
                ],
                keep="last",
            )
            .sort_values(
                by=[
                    "stock_code",
                    "date",
                ]
            )
            .reset_index(drop=True)
        )

        COMBINED_OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        combined_data.to_csv(
            COMBINED_OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"\n[SAVED] Combined valuation data: " f"{COMBINED_OUTPUT_PATH}")

    stock_summary_data = pd.DataFrame(stock_summary_records)

    indicator_summary_data = pd.DataFrame(indicator_summary_records)

    SUMMARY_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    stock_summary_data.to_csv(
        SUMMARY_OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    indicator_summary_path = (
        SUMMARY_OUTPUT_PATH.parent / "valuation_indicator_summary.csv"
    )

    indicator_summary_data.to_csv(
        indicator_summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Stock summary: " f"{SUMMARY_OUTPUT_PATH}")

    print(f"[SAVED] Indicator summary: " f"{indicator_summary_path}")

    print("\n========== VALUATION SUMMARY ==========")

    if not stock_summary_data.empty:
        display_columns = [
            "stock_code",
            "status",
            "rows",
            "earliest_date",
            "latest_date",
            "missing_pe_ttm",
            "missing_pe_static",
            "missing_pb",
            "missing_total_market_value",
        ]

        existing_display_columns = [
            column for column in display_columns if column in stock_summary_data.columns
        ]

        print(stock_summary_data[existing_display_columns].to_string(index=False))


if __name__ == "__main__":
    process_all_stock_valuations()
