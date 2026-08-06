from collections.abc import Callable
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

STATEMENT_TYPES = [
    "资产负债表",
    "利润表",
    "现金流量表",
]

STATEMENT_DIRECTORY_MAP = {
    "资产负债表": "balance_sheet",
    "利润表": "income_statement",
    "现金流量表": "cash_flow_statement",
}

STATEMENT_INTERFACE_MAP: dict[
    str,
    Callable[..., pd.DataFrame],
] = {
    "资产负债表": ak.stock_balance_sheet_by_report_em,
    "利润表": ak.stock_profit_sheet_by_report_em,
    "现金流量表": ak.stock_cash_flow_sheet_by_report_em,
}


def normalize_a_stock_code(
    stock_code: str,
) -> str:
    normalized_code = stock_code.strip().upper()

    if (
        len(normalized_code) != 8
        or normalized_code[:2] not in {"SH", "SZ", "BJ"}
        or not normalized_code[2:].isdigit()
    ):
        raise ValueError(
            "Invalid A-share stock code: "
            f"{stock_code}. Expected formats such as "
            "'SZ002067' or 'SH600763'."
        )

    return normalized_code


def fetch_a_financial_report(
    stock_code: str,
    statement_type: str,
    max_retries: int = 3,
) -> pd.DataFrame:
    normalized_code = normalize_a_stock_code(stock_code)

    if statement_type not in STATEMENT_INTERFACE_MAP:
        raise ValueError(f"Unsupported statement type: {statement_type}")

    fetch_interface = STATEMENT_INTERFACE_MAP[statement_type]

    for attempt in range(1, max_retries + 1):
        try:
            financial_data: pd.DataFrame = fetch_interface(
                symbol=normalized_code,
            )

            if financial_data.empty:
                raise RuntimeError(
                    f"No data returned for " f"{normalized_code} " f"{statement_type}."
                )

            return financial_data

        except Exception as error:
            print(
                f"[RETRY {attempt}/{max_retries}] "
                f"{normalized_code} "
                f"{statement_type}: {error}"
            )

            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to fetch "
                    f"{statement_type} for "
                    f"A-share stock "
                    f"{normalized_code}."
                ) from error

            time.sleep(3)

    raise RuntimeError(
        f"Unexpected fetch failure: " f"{normalized_code} " f"{statement_type}."
    )


def clean_a_financial_report(
    data: pd.DataFrame,
    statement_type: str,
) -> pd.DataFrame:
    cleaned_data = data.copy()

    cleaned_data.columns = cleaned_data.columns.astype(str).str.strip()

    cleaned_data = cleaned_data.replace(
        {
            "-": pd.NA,
            "--": pd.NA,
            "": pd.NA,
        }
    )

    if "REPORT_DATE" not in cleaned_data.columns:
        raise KeyError("REPORT_DATE does not exist " "in the returned financial data.")

    # 转换所有以 _DATE 结尾的日期字段
    date_columns = [
        column for column in cleaned_data.columns if column.endswith("_DATE")
    ]

    for date_column in date_columns:
        cleaned_data[date_column] = pd.to_datetime(
            cleaned_data[date_column],
            errors="coerce",
        )

    cleaned_data = cleaned_data.rename(
        columns={
            "SECUCODE": "security_id",
            "SECURITY_CODE": "stock_code",
            "SECURITY_NAME_ABBR": "stock_name",
            "ORG_CODE": "organization_code",
            "REPORT_DATE": "report_date",
            "REPORT_TYPE": "report_type",
            "REPORT_DATE_NAME": "report_date_name",
            "NOTICE_DATE": "notice_date",
            "UPDATE_DATE": "update_date",
        }
    )

    cleaned_data["stock_code"] = cleaned_data["stock_code"].astype(str).str.zfill(6)

    cleaned_data["statement_type"] = statement_type

    cleaned_data["currency"] = "CNY"

    required_columns = [
        "stock_code",
        "report_date",
    ]

    cleaned_data = cleaned_data.dropna(subset=required_columns)

    duplicate_columns = [
        "stock_code",
        "statement_type",
        "report_date",
    ]

    if "report_type" in cleaned_data.columns:
        duplicate_columns.append("report_type")

    cleaned_data = cleaned_data.drop_duplicates(
        subset=duplicate_columns,
        keep="last",
    )

    sort_columns = [
        "report_date",
    ]

    if "report_type" in cleaned_data.columns:
        sort_columns.append("report_type")

    cleaned_data = cleaned_data.sort_values(
        by=sort_columns,
        ascending=False,
    ).reset_index(drop=True)

    # 把常用识别字段放在最前面，
    # 其余数百个财务字段全部保留
    preferred_columns = [
        "security_id",
        "stock_code",
        "stock_name",
        "organization_code",
        "statement_type",
        "currency",
        "report_date",
        "report_type",
        "report_date_name",
        "notice_date",
        "update_date",
    ]

    existing_preferred_columns = [
        column for column in preferred_columns if column in cleaned_data.columns
    ]

    remaining_columns = [
        column
        for column in cleaned_data.columns
        if column not in existing_preferred_columns
    ]

    cleaned_data = cleaned_data[existing_preferred_columns + remaining_columns]

    return cleaned_data


def store_a_financial_report(
    stock_code: str,
    statement_type: str,
    raw_data: pd.DataFrame,
    cleaned_data: pd.DataFrame,
) -> tuple[Path, Path]:
    normalized_code = normalize_a_stock_code(stock_code)

    directory_name = STATEMENT_DIRECTORY_MAP[statement_type]

    raw_directory = PROJECT_ROOT / "data" / "raw" / "a_share" / directory_name

    cleaned_directory = PROJECT_ROOT / "data" / "cleaned" / "a_share" / directory_name

    raw_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename_code = normalized_code.lower()

    raw_path = raw_directory / f"{filename_code}_{directory_name}_report.csv"

    cleaned_path = cleaned_directory / f"{filename_code}_{directory_name}_report.csv"

    raw_data.to_csv(
        raw_path,
        index=False,
        encoding="utf-8-sig",
    )

    cleaned_data.to_csv(
        cleaned_path,
        index=False,
        encoding="utf-8-sig",
    )

    return raw_path, cleaned_path


def build_fetch_summary(
    stock_code: str,
    statement_type: str,
    data: pd.DataFrame,
    status: str,
    error_message: str = "",
) -> dict:
    normalized_code = normalize_a_stock_code(stock_code)

    if data.empty:
        return {
            "stock_code": normalized_code,
            "statement_type": statement_type,
            "status": status,
            "rows": 0,
            "columns": 0,
            "report_periods": 0,
            "missing_cells": 0,
            "earliest_report": pd.NaT,
            "latest_report": pd.NaT,
            "error_message": error_message,
        }

    return {
        "stock_code": normalized_code,
        "statement_type": statement_type,
        "status": status,
        "rows": len(data),
        "columns": len(data.columns),
        "report_periods": (data["report_date"].nunique()),
        "missing_cells": int(data.isna().sum().sum()),
        "earliest_report": (data["report_date"].min()),
        "latest_report": (data["report_date"].max()),
        "error_message": error_message,
    }


def process_a_stock(
    stock_code: str,
) -> list[dict]:
    normalized_code = normalize_a_stock_code(stock_code)

    stock_summary: list[dict] = []

    print(f"\n[START] A-share stock: " f"{normalized_code}")

    for statement_type in STATEMENT_TYPES:
        try:
            raw_data = fetch_a_financial_report(
                stock_code=normalized_code,
                statement_type=statement_type,
            )

            cleaned_data = clean_a_financial_report(
                data=raw_data,
                statement_type=statement_type,
            )

            raw_path, cleaned_path = store_a_financial_report(
                stock_code=normalized_code,
                statement_type=statement_type,
                raw_data=raw_data,
                cleaned_data=cleaned_data,
            )

            stock_summary.append(
                build_fetch_summary(
                    stock_code=normalized_code,
                    statement_type=statement_type,
                    data=cleaned_data,
                    status="success",
                )
            )

            print(
                f"[SUCCESS] "
                f"{normalized_code} "
                f"{statement_type}: "
                f"{len(cleaned_data)} rows, "
                f"{len(cleaned_data.columns)} columns"
            )

            print(f"          Raw: " f"{raw_path}")

            print(f"          Cleaned: " f"{cleaned_path}")

        except Exception as error:
            stock_summary.append(
                build_fetch_summary(
                    stock_code=normalized_code,
                    statement_type=statement_type,
                    data=pd.DataFrame(),
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED] " f"{normalized_code} " f"{statement_type}: " f"{error}")

        time.sleep(1)

    return stock_summary


def process_all_a_stocks() -> None:
    all_summary: list[dict] = []

    for stock_code in A_STOCK_CODES:
        stock_summary = process_a_stock(
            stock_code=stock_code,
        )

        all_summary.extend(stock_summary)

    summary_data = pd.DataFrame(all_summary)

    summary_directory = PROJECT_ROOT / "data" / "summary"

    summary_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = summary_directory / "a_share_financial_fetch_summary.csv"

    summary_data.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n========== FETCH SUMMARY ==========")

    if not summary_data.empty:
        display_columns = [
            "stock_code",
            "statement_type",
            "status",
            "rows",
            "columns",
            "report_periods",
            "missing_cells",
        ]

        print(summary_data[display_columns].to_string(index=False))

    print(f"\n[SAVED] Summary: " f"{summary_path}")


if __name__ == "__main__":
    process_all_a_stocks()
