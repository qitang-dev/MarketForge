from pathlib import Path
import time

import akshare as ak
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HK_STOCK_CODES = [
    "02180",
    "08365",
    "08462",
    "02076",
    "06100",
    "06919",
    "09669",
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

CURRENCY_MAP = {
    "02180": "CNY",
    "08365": "CNY",
    "08462": "CNY",
    "02076": "CNY",
    "06100": "CNY",
    "06919": "CNY",
    "09669": "CNY",
}


def fetch_hk_financial_report(
    stock_code: str,
    statement_type: str,
    period_type: str = "年度",
    max_retries: int = 3,
) -> pd.DataFrame:
    for attempt in range(1, max_retries + 1):
        try:
            financial_data: pd.DataFrame = ak.stock_financial_hk_report_em(
                stock=stock_code,
                symbol=statement_type,
                indicator=period_type,
            )

            if financial_data.empty:
                raise RuntimeError(
                    f"No data returned for " f"{stock_code} {statement_type}."
                )

            return financial_data

        except Exception as error:
            print(
                f"[RETRY {attempt}/{max_retries}] "
                f"{stock_code} {statement_type}: {error}"
            )

            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to fetch {statement_type} " f"for HK stock {stock_code}."
                ) from error

            time.sleep(3)

    raise RuntimeError(f"Unexpected fetch failure: " f"{stock_code} {statement_type}.")


def clean_hk_financial_report(
    data: pd.DataFrame,
    statement_type: str,
) -> pd.DataFrame:
    cleaned_data = data.copy()

    cleaned_data.columns = cleaned_data.columns.astype(str).str.strip()

    if "STD_REPORT_DATE" in cleaned_data.columns:
        report_date_column = "STD_REPORT_DATE"

    elif "REPORT_DATE" in cleaned_data.columns:
        report_date_column = "REPORT_DATE"

    else:
        raise KeyError(
            "Neither STD_REPORT_DATE nor REPORT_DATE " "exists in the returned data."
        )

    cleaned_data["report_date"] = pd.to_datetime(
        cleaned_data[report_date_column],
        errors="coerce",
    )

    if "START_DATE" in cleaned_data.columns:
        cleaned_data["start_date"] = pd.to_datetime(
            cleaned_data["START_DATE"],
            errors="coerce",
        )
    else:
        cleaned_data["start_date"] = pd.NaT

    cleaned_data["amount"] = pd.to_numeric(
        cleaned_data["AMOUNT"],
        errors="coerce",
    )

    cleaned_data["statement_type"] = statement_type

    cleaned_data = cleaned_data.rename(
        columns={
            "SECUCODE": "security_id",
            "SECURITY_CODE": "stock_code",
            "SECURITY_NAME_ABBR": "stock_name",
            "ORG_CODE": "organization_code",
            "FISCAL_YEAR": "fiscal_year",
            "STD_ITEM_CODE": "item_code",
            "STD_ITEM_NAME": "item_name",
        }
    )

    cleaned_data["currency"] = (
        cleaned_data["stock_code"].astype(str).str.zfill(5).map(CURRENCY_MAP)
    )

    if cleaned_data["currency"].isna().any():
        missing_codes = (
            cleaned_data.loc[
                cleaned_data["currency"].isna(),
                "stock_code",
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(f"Missing currency mapping for: {missing_codes}")

    selected_columns = [
        "security_id",
        "stock_code",
        "stock_name",
        "organization_code",
        "statement_type",
        "currency",
        "report_date",
        "start_date",
        "fiscal_year",
        "item_code",
        "item_name",
        "amount",
    ]

    cleaned_data = cleaned_data[selected_columns]

    cleaned_data = cleaned_data.dropna(
        subset=[
            "stock_code",
            "report_date",
            "item_code",
            "item_name",
        ]
    )

    cleaned_data = cleaned_data.drop_duplicates(
        subset=[
            "stock_code",
            "statement_type",
            "report_date",
            "item_code",
        ],
        keep="last",
    )

    cleaned_data = cleaned_data.sort_values(
        by=[
            "report_date",
            "item_code",
        ]
    ).reset_index(drop=True)

    return cleaned_data


def store_hk_financial_report(
    stock_code: str,
    statement_type: str,
    raw_data: pd.DataFrame,
    cleaned_data: pd.DataFrame,
) -> tuple[Path, Path]:
    directory_name = STATEMENT_DIRECTORY_MAP[statement_type]

    raw_directory = PROJECT_ROOT / "data" / "raw" / "hk" / directory_name

    cleaned_directory = PROJECT_ROOT / "data" / "cleaned" / "hk" / directory_name

    raw_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_path = raw_directory / f"{stock_code}_{directory_name}_annual.csv"

    cleaned_path = cleaned_directory / f"{stock_code}_{directory_name}_annual.csv"

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
    if data.empty:
        return {
            "stock_code": stock_code,
            "statement_type": statement_type,
            "status": status,
            "rows": 0,
            "report_periods": 0,
            "unique_items": 0,
            "missing_amounts": 0,
            "earliest_report": pd.NaT,
            "latest_report": pd.NaT,
            "error_message": error_message,
        }

    return {
        "stock_code": stock_code,
        "statement_type": statement_type,
        "status": status,
        "rows": len(data),
        "report_periods": data["report_date"].nunique(),
        "unique_items": data["item_code"].nunique(),
        "missing_amounts": data["amount"].isna().sum(),
        "earliest_report": data["report_date"].min(),
        "latest_report": data["report_date"].max(),
        "error_message": error_message,
    }


def process_hk_stock(
    stock_code: str,
) -> list[dict]:
    stock_summary: list[dict] = []

    print(f"\n[START] HK stock: {stock_code}")

    for statement_type in STATEMENT_TYPES:
        try:
            raw_data = fetch_hk_financial_report(
                stock_code=stock_code,
                statement_type=statement_type,
            )

            cleaned_data = clean_hk_financial_report(
                data=raw_data,
                statement_type=statement_type,
            )

            raw_path, cleaned_path = store_hk_financial_report(
                stock_code=stock_code,
                statement_type=statement_type,
                raw_data=raw_data,
                cleaned_data=cleaned_data,
            )

            stock_summary.append(
                build_fetch_summary(
                    stock_code=stock_code,
                    statement_type=statement_type,
                    data=cleaned_data,
                    status="success",
                )
            )

            print(
                f"[SUCCESS] {stock_code} "
                f"{statement_type}: "
                f"{len(cleaned_data)} rows"
            )
            print(f"          Raw: {raw_path}")
            print(f"          Cleaned: {cleaned_path}")

        except Exception as error:
            stock_summary.append(
                build_fetch_summary(
                    stock_code=stock_code,
                    statement_type=statement_type,
                    data=pd.DataFrame(),
                    status="failed",
                    error_message=str(error),
                )
            )

            print(f"[FAILED] {stock_code} " f"{statement_type}: {error}")

        time.sleep(1)

    return stock_summary


def process_all_hk_stocks() -> None:
    all_summary: list[dict] = []

    for stock_code in HK_STOCK_CODES:
        stock_summary = process_hk_stock(
            stock_code=stock_code,
        )

        all_summary.extend(stock_summary)

    summary_data = pd.DataFrame(all_summary)

    summary_directory = PROJECT_ROOT / "data" / "summary"

    summary_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = summary_directory / "hk_financial_fetch_summary.csv"

    summary_data.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n========== FETCH SUMMARY ==========")

    if not summary_data.empty:
        print(
            summary_data[
                [
                    "stock_code",
                    "statement_type",
                    "status",
                    "rows",
                    "report_periods",
                    "unique_items",
                    "missing_amounts",
                ]
            ].to_string(index=False)
        )

    print(f"\n[SAVED] Summary: {summary_path}")


if __name__ == "__main__":
    process_all_hk_stocks()
