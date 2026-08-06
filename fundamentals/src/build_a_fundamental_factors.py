from pathlib import Path

import numpy as np
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


STATEMENT_DIRECTORIES = {
    "balance_sheet": (PROJECT_ROOT / "data" / "cleaned" / "a_share" / "balance_sheet"),
    "income_statement": (
        PROJECT_ROOT / "data" / "cleaned" / "a_share" / "income_statement"
    ),
    "cash_flow_statement": (
        PROJECT_ROOT / "data" / "cleaned" / "a_share" / "cash_flow_statement"
    ),
}


INDIVIDUAL_FACTOR_DIRECTORY = (
    PROJECT_ROOT / "data" / "factors" / "a_share" / "individual"
)

COMBINED_FACTOR_PATH = (
    PROJECT_ROOT / "data" / "factors" / "a_share" / "a_share_fundamental_factors.csv"
)

SUMMARY_PATH = PROJECT_ROOT / "data" / "summary" / "a_share_factor_build_summary.csv"


FIELD_MAP = {
    # Income statement
    "revenue": "TOTAL_OPERATE_INCOME",
    "revenue_yoy": "TOTAL_OPERATE_INCOME_YOY",
    "operating_revenue": "OPERATE_INCOME",
    "operating_cost": "OPERATE_COST",
    "net_profit": "NETPROFIT",
    "parent_net_profit": "PARENT_NETPROFIT",
    "parent_net_profit_yoy": "PARENT_NETPROFIT_YOY",
    # Balance sheet
    "total_assets": "TOTAL_ASSETS",
    "total_assets_growth": "TOTAL_ASSETS_YOY",
    "total_liabilities": "TOTAL_LIABILITIES",
    "total_current_assets": "TOTAL_CURRENT_ASSETS",
    "total_current_liabilities": "TOTAL_CURRENT_LIAB",
    "parent_equity": "TOTAL_PARENT_EQUITY",
    "total_equity": "TOTAL_EQUITY",
    # Cash flow statement
    "operating_cash_flow": "NETCASH_OPERATE",
}


PERCENTAGE_SOURCE_FIELDS = {
    "revenue_yoy",
    "parent_net_profit_yoy",
    "total_assets_growth",
}


FINAL_COLUMNS = [
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
    "operating_revenue",
    "operating_cost",
    "gross_margin",
    "net_margin",
    "total_assets",
    "total_assets_growth",
    "total_liabilities",
    "debt_to_asset_ratio",
    "total_current_assets",
    "total_current_liabilities",
    "current_ratio",
    "parent_equity",
    "total_equity",
    "average_parent_equity",
    "roe",
    "roe_ending_equity",
    "operating_cash_flow",
    "operating_cash_flow_to_net_profit",
]


def build_statement_path(
    stock_code: str,
    statement_name: str,
) -> Path:
    directory = STATEMENT_DIRECTORIES[statement_name]

    return directory / f"{stock_code}_{statement_name}_report.csv"


def load_statement(
    stock_code: str,
    statement_name: str,
) -> pd.DataFrame:
    file_path = build_statement_path(
        stock_code=stock_code,
        statement_name=statement_name,
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Statement file does not exist: {file_path}")

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
    )

    data.columns = data.columns.astype(str).str.strip()

    required_columns = [
        "stock_code",
        "report_date",
    ]

    missing_columns = [
        column for column in required_columns if column not in data.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing required columns in {file_path}: " f"{missing_columns}"
        )

    data["stock_code"] = data["stock_code"].astype(str).str.zfill(6)

    data["report_date"] = pd.to_datetime(
        data["report_date"],
        errors="coerce",
    )

    if "notice_date" in data.columns:
        data["notice_date"] = pd.to_datetime(
            data["notice_date"],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "stock_code",
            "report_date",
        ]
    )

    data = data.drop_duplicates(
        subset=[
            "stock_code",
            "report_date",
        ],
        keep="last",
    )

    return data


def validate_source_fields(
    data: pd.DataFrame,
    required_fields: list[str],
    statement_name: str,
) -> None:
    missing_fields = [
        FIELD_MAP[field_name]
        for field_name in required_fields
        if FIELD_MAP[field_name] not in data.columns
    ]

    if missing_fields:
        raise KeyError(
            f"Missing source fields in {statement_name}: " f"{missing_fields}"
        )


def normalize_percentage_series(
    data: pd.Series,
) -> pd.Series:
    numeric_data = pd.to_numeric(
        data,
        errors="coerce",
    )

    non_missing_data = numeric_data.dropna()

    if non_missing_data.empty:
        return numeric_data

    median_absolute_value = non_missing_data.abs().median()

    # 财报接口中的同比字段通常以百分数形式存储：
    # 12.5 表示 12.5%，因此转换为 0.125。
    if median_absolute_value > 1:
        numeric_data = numeric_data / 100

    return numeric_data


def safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    numeric_numerator = pd.to_numeric(
        numerator,
        errors="coerce",
    )

    numeric_denominator = pd.to_numeric(
        denominator,
        errors="coerce",
    )

    result = numeric_numerator / (
        numeric_denominator.replace(
            0,
            np.nan,
        )
    )

    result = result.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    return result


def build_base_data(
    income_data: pd.DataFrame,
) -> pd.DataFrame:
    base_columns = [
        "stock_code",
        "stock_name",
        "report_date",
        "notice_date",
        "report_type",
        "currency",
    ]

    existing_columns = [
        column for column in base_columns if column in income_data.columns
    ]

    base_data = (
        income_data[existing_columns]
        .copy()
        .drop_duplicates(
            subset=[
                "stock_code",
                "report_date",
            ],
            keep="last",
        )
    )

    return base_data


def extract_fields(
    data: pd.DataFrame,
    field_names: list[str],
    statement_name: str,
) -> pd.DataFrame:
    validate_source_fields(
        data=data,
        required_fields=field_names,
        statement_name=statement_name,
    )

    result = data[
        [
            "stock_code",
            "report_date",
        ]
    ].copy()

    for field_name in field_names:
        source_column = FIELD_MAP[field_name]

        numeric_data = pd.to_numeric(
            data[source_column],
            errors="coerce",
        )

        if field_name in PERCENTAGE_SOURCE_FIELDS:
            numeric_data = normalize_percentage_series(numeric_data)

        result[field_name] = numeric_data

    result = result.drop_duplicates(
        subset=[
            "stock_code",
            "report_date",
        ],
        keep="last",
    )

    return result


def extract_income_fields(
    income_data: pd.DataFrame,
) -> pd.DataFrame:
    income_fields = [
        "revenue",
        "revenue_yoy",
        "operating_revenue",
        "operating_cost",
        "net_profit",
        "parent_net_profit",
        "parent_net_profit_yoy",
    ]

    return extract_fields(
        data=income_data,
        field_names=income_fields,
        statement_name="income_statement",
    )


def extract_balance_fields(
    balance_data: pd.DataFrame,
) -> pd.DataFrame:
    balance_fields = [
        "total_assets",
        "total_assets_growth",
        "total_liabilities",
        "total_current_assets",
        "total_current_liabilities",
        "parent_equity",
        "total_equity",
    ]

    return extract_fields(
        data=balance_data,
        field_names=balance_fields,
        statement_name="balance_sheet",
    )


def extract_cash_flow_fields(
    cash_flow_data: pd.DataFrame,
) -> pd.DataFrame:
    cash_flow_fields = [
        "operating_cash_flow",
    ]

    return extract_fields(
        data=cash_flow_data,
        field_names=cash_flow_fields,
        statement_name="cash_flow_statement",
    )


def merge_statement_fields(
    base_data: pd.DataFrame,
    income_fields: pd.DataFrame,
    balance_fields: pd.DataFrame,
    cash_flow_fields: pd.DataFrame,
) -> pd.DataFrame:
    merge_keys = [
        "stock_code",
        "report_date",
    ]

    result = base_data.merge(
        income_fields,
        on=merge_keys,
        how="left",
        validate="one_to_one",
    )

    result = result.merge(
        balance_fields,
        on=merge_keys,
        how="left",
        validate="one_to_one",
    )

    result = result.merge(
        cash_flow_fields,
        on=merge_keys,
        how="left",
        validate="one_to_one",
    )

    return result


def calculate_average_parent_equity(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    result["report_month_day"] = result["report_date"].dt.strftime("%m-%d")

    result = result.sort_values(
        by=[
            "stock_code",
            "report_month_day",
            "report_date",
        ]
    ).reset_index(drop=True)

    previous_parent_equity = result.groupby(
        [
            "stock_code",
            "report_month_day",
        ]
    )[
        "parent_equity"
    ].shift(1)

    result["average_parent_equity"] = (
        result["parent_equity"] + previous_parent_equity
    ) / 2

    result = result.drop(
        columns=[
            "report_month_day",
        ]
    )

    return result


def calculate_financial_factors(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = data.copy()

    # 毛利率
    result["gross_margin"] = safe_divide(
        result["operating_revenue"] - result["operating_cost"],
        result["operating_revenue"],
    )

    # 净利率
    result["net_margin"] = safe_divide(
        result["net_profit"],
        result["revenue"],
    )

    # 资产负债率
    result["debt_to_asset_ratio"] = safe_divide(
        result["total_liabilities"],
        result["total_assets"],
    )

    # 流动比率
    result["current_ratio"] = safe_divide(
        result["total_current_assets"],
        result["total_current_liabilities"],
    )

    # 经营活动现金流量净额 / 净利润
    result["operating_cash_flow_to_net_profit"] = safe_divide(
        result["operating_cash_flow"],
        result["net_profit"],
    )

    result = calculate_average_parent_equity(
        data=result,
    )

    # 使用平均归母股东权益计算ROE
    result["roe"] = safe_divide(
        result["parent_net_profit"],
        result["average_parent_equity"],
    )

    # 保留期末权益口径，便于校验
    result["roe_ending_equity"] = safe_divide(
        result["parent_net_profit"],
        result["parent_equity"],
    )

    return result


def select_final_columns(
    data: pd.DataFrame,
) -> pd.DataFrame:
    existing_columns = [column for column in FINAL_COLUMNS if column in data.columns]

    result = data[existing_columns].copy()

    result = result.sort_values(
        by=[
            "stock_code",
            "report_date",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)

    return result


def build_stock_factor_data(
    stock_code: str,
) -> pd.DataFrame:
    balance_data = load_statement(
        stock_code=stock_code,
        statement_name="balance_sheet",
    )

    income_data = load_statement(
        stock_code=stock_code,
        statement_name="income_statement",
    )

    cash_flow_data = load_statement(
        stock_code=stock_code,
        statement_name="cash_flow_statement",
    )

    base_data = build_base_data(
        income_data=income_data,
    )

    income_fields = extract_income_fields(
        income_data=income_data,
    )

    balance_fields = extract_balance_fields(
        balance_data=balance_data,
    )

    cash_flow_fields = extract_cash_flow_fields(
        cash_flow_data=cash_flow_data,
    )

    merged_data = merge_statement_fields(
        base_data=base_data,
        income_fields=income_fields,
        balance_fields=balance_fields,
        cash_flow_fields=cash_flow_fields,
    )

    factor_data = calculate_financial_factors(
        data=merged_data,
    )

    factor_data = select_final_columns(
        data=factor_data,
    )

    return factor_data


def store_stock_factor_data(
    stock_code: str,
    factor_data: pd.DataFrame,
) -> Path:
    INDIVIDUAL_FACTOR_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = INDIVIDUAL_FACTOR_DIRECTORY / f"{stock_code}_fundamental_factors.csv"

    factor_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def build_summary_record(
    stock_code: str,
    factor_data: pd.DataFrame,
    status: str,
    error_message: str = "",
) -> dict:
    if factor_data.empty:
        return {
            "stock_code": stock_code,
            "status": status,
            "rows": 0,
            "columns": 0,
            "report_periods": 0,
            "earliest_report": pd.NaT,
            "latest_report": pd.NaT,
            "missing_values": 0,
            "error_message": error_message,
        }

    return {
        "stock_code": stock_code,
        "status": status,
        "rows": len(factor_data),
        "columns": len(factor_data.columns),
        "report_periods": (factor_data["report_date"].nunique()),
        "earliest_report": (factor_data["report_date"].min()),
        "latest_report": (factor_data["report_date"].max()),
        "missing_values": int(factor_data.isna().sum().sum()),
        "error_message": error_message,
    }


def process_all_stock_factors() -> None:
    all_factor_data: list[pd.DataFrame] = []
    summary_records: list[dict] = []

    for stock_code in A_STOCK_CODES:
        print(f"\n[START] Building factors: " f"{stock_code}")

        try:
            factor_data = build_stock_factor_data(
                stock_code=stock_code,
            )

            output_path = store_stock_factor_data(
                stock_code=stock_code,
                factor_data=factor_data,
            )

            all_factor_data.append(factor_data)

            summary_records.append(
                build_summary_record(
                    stock_code=stock_code,
                    factor_data=factor_data,
                    status="success",
                )
            )

            print(f"[SUCCESS] {stock_code}: " f"{len(factor_data)} rows")

            print(f"          Saved: {output_path}")

        except Exception as error:
            summary_records.append(
                build_summary_record(
                    stock_code=stock_code,
                    factor_data=pd.DataFrame(),
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED] {stock_code}: " f"{error}")

    if all_factor_data:
        combined_factor_data = pd.concat(
            all_factor_data,
            ignore_index=True,
        )

        combined_factor_data = combined_factor_data.sort_values(
            by=[
                "stock_code",
                "report_date",
            ],
            ascending=[
                True,
                False,
            ],
        ).reset_index(drop=True)

        COMBINED_FACTOR_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        combined_factor_data.to_csv(
            COMBINED_FACTOR_PATH,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"\n[SAVED] Combined factor data: " f"{COMBINED_FACTOR_PATH}")

    summary_data = pd.DataFrame(summary_records)

    SUMMARY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_data.to_csv(
        SUMMARY_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Factor build summary: " f"{SUMMARY_PATH}")

    print("\n========== FACTOR BUILD SUMMARY ==========")

    if not summary_data.empty:
        display_columns = [
            "stock_code",
            "status",
            "rows",
            "columns",
            "report_periods",
            "missing_values",
        ]

        print(summary_data[display_columns].to_string(index=False))


if __name__ == "__main__":
    process_all_stock_factors()
