from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEST_STOCK_CODE = "sz002067"

STATEMENT_DIRECTORIES = {
    "balance_sheet": (PROJECT_ROOT / "data" / "cleaned" / "a_share" / "balance_sheet"),
    "income_statement": (
        PROJECT_ROOT / "data" / "cleaned" / "a_share" / "income_statement"
    ),
    "cash_flow_statement": (
        PROJECT_ROOT / "data" / "cleaned" / "a_share" / "cash_flow_statement"
    ),
}

OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "inspection" / "factor_fields"

BALANCE_SHEET_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "a_share"
    / "balance_sheet"
    / "sz002067_balance_sheet_report.csv"
)


FIELD_KEYWORDS = {
    "income_statement": {
        "revenue": [
            "TOTAL_OPERATE_INCOME",
            "OPERATE_INCOME",
            "REVENUE",
        ],
        "revenue_yoy": [
            "TOTAL_OPERATE_INCOME_YOY",
            "OPERATE_INCOME_YOY",
            "REVENUE_YOY",
        ],
        "parent_net_profit": [
            "PARENT_NETPROFIT",
            "PARENT_NET_PROFIT",
        ],
        "parent_net_profit_yoy": [
            "PARENT_NETPROFIT_YOY",
            "PARENT_NET_PROFIT_YOY",
        ],
        "net_profit": [
            "NETPROFIT",
            "NET_PROFIT",
        ],
        "operating_cost": [
            "OPERATE_COST",
            "TOTAL_OPERATE_COST",
            "COST",
        ],
        "gross_profit": [
            "GROSS_PROFIT",
        ],
        "gross_margin": [
            "GROSS_MARGIN",
        ],
        "net_margin": [
            "NET_MARGIN",
            "NET_PROFIT_MARGIN",
        ],
        "roe": [
            "ROE",
            "WEIGHTED_ROE",
        ],
    },
    "balance_sheet": {
        "total_assets": [
            "TOTAL_ASSETS",
        ],
        "total_assets_yoy": [
            "TOTAL_ASSETS_YOY",
        ],
        "total_liabilities": [
            "TOTAL_LIABILITIES",
            "TOTAL_LIAB",
        ],
        "current_assets": [
            "TOTAL_CURRENT_ASSETS",
            "CURRENT_ASSETS",
        ],
        "current_liabilities": [
            "TOTAL_CURRENT_LIABILITIES",
            "CURRENT_LIABILITIES",
        ],
        "parent_equity": [
            "TOTAL_EQUITY_PARENT",
            "PARENT_HOLDER_EQUITY",
            "TOTAL_PARENT_EQUITY",
        ],
        "total_equity": [
            "TOTAL_EQUITY",
            "TOTAL_HOLDER_EQUITY",
        ],
        "debt_to_asset_ratio": [
            "DEBT_ASSET_RATIO",
            "ASSET_LIABILITY_RATIO",
        ],
        "current_ratio": [
            "CURRENT_RATIO",
        ],
        "roe": [
            "ROE",
            "WEIGHTED_ROE",
        ],
    },
    "cash_flow_statement": {
        "operating_cash_flow": [
            "NETCASH_OPERATE",
            "NET_CASH_OPERATE",
            "NETCASH_OPERATING",
            "OPERATE_CASH_FLOW",
        ],
    },
}


def build_statement_path(
    stock_code: str,
    statement_name: str,
) -> Path:
    directory = STATEMENT_DIRECTORIES[statement_name]

    return directory / f"{stock_code}_{statement_name}_report.csv"


def load_statement_columns(
    stock_code: str,
    statement_name: str,
) -> list[str]:
    file_path = build_statement_path(
        stock_code=stock_code,
        statement_name=statement_name,
    )

    if not file_path.exists():
        raise FileNotFoundError(f"Statement file does not exist: {file_path}")

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        nrows=5,
    )

    columns = data.columns.astype(str).str.strip().tolist()

    return columns


def find_matching_columns(
    columns: list[str],
    keywords: list[str],
) -> list[str]:
    matches: list[str] = []

    for column in columns:
        upper_column = column.upper()

        for keyword in keywords:
            if keyword.upper() in upper_column:
                matches.append(column)
                break

    return matches


def inspect_statement_fields(
    stock_code: str,
    statement_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = load_statement_columns(
        stock_code=stock_code,
        statement_name=statement_name,
    )

    field_records: list[dict] = []

    for factor_name, keywords in FIELD_KEYWORDS[statement_name].items():
        matching_columns = find_matching_columns(
            columns=columns,
            keywords=keywords,
        )

        field_records.append(
            {
                "stock_code": stock_code,
                "statement_name": statement_name,
                "factor_name": factor_name,
                "keywords": " | ".join(keywords),
                "matching_columns": (" | ".join(matching_columns)),
                "match_count": len(matching_columns),
                "status": ("found" if matching_columns else "missing"),
            }
        )

    field_result = pd.DataFrame(field_records)

    all_columns_result = pd.DataFrame(
        {
            "stock_code": stock_code,
            "statement_name": statement_name,
            "column_position": range(
                1,
                len(columns) + 1,
            ),
            "column_name": columns,
        }
    )

    return field_result, all_columns_result


def inspect_all_factor_fields(
    stock_code: str,
) -> None:
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_field_results: list[pd.DataFrame] = []
    all_column_results: list[pd.DataFrame] = []

    for statement_name in STATEMENT_DIRECTORIES:
        try:
            field_result, column_result = inspect_statement_fields(
                stock_code=stock_code,
                statement_name=statement_name,
            )

            all_field_results.append(field_result)

            all_column_results.append(column_result)

            print(f"\n========== {statement_name.upper()} ==========")

            print(
                field_result[
                    [
                        "factor_name",
                        "matching_columns",
                        "match_count",
                        "status",
                    ]
                ].to_string(index=False)
            )

        except Exception as error:
            print(f"[FAILED] {statement_name}: {error}")

    if not all_field_results:
        raise RuntimeError("No financial statement fields were inspected.")

    combined_field_result = pd.concat(
        all_field_results,
        ignore_index=True,
    )

    combined_column_result = pd.concat(
        all_column_results,
        ignore_index=True,
    )

    field_output_path = OUTPUT_DIRECTORY / f"{stock_code}_factor_field_matches.csv"

    column_output_path = OUTPUT_DIRECTORY / f"{stock_code}_all_statement_columns.csv"

    missing_output_path = OUTPUT_DIRECTORY / f"{stock_code}_missing_factor_fields.csv"

    combined_field_result.to_csv(
        field_output_path,
        index=False,
        encoding="utf-8-sig",
    )

    combined_column_result.to_csv(
        column_output_path,
        index=False,
        encoding="utf-8-sig",
    )

    missing_fields = combined_field_result[
        combined_field_result["status"] == "missing"
    ].copy()

    missing_fields.to_csv(
        missing_output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n========== INSPECTION SUMMARY ==========")

    print(
        combined_field_result[
            [
                "statement_name",
                "factor_name",
                "matching_columns",
                "status",
            ]
        ].to_string(index=False)
    )

    print(f"\n[SAVED] Field matches: " f"{field_output_path}")

    print(f"[SAVED] All columns: " f"{column_output_path}")

    print(f"[SAVED] Missing fields: " f"{missing_output_path}")


def inspect_current_liability_fields() -> None:
    balance_data = pd.read_csv(
        BALANCE_SHEET_PATH,
        encoding="utf-8-sig",
        nrows=5,
    )

    balance_data.columns = balance_data.columns.astype(str).str.strip()

    matching_columns = [
        column
        for column in balance_data.columns
        if ("CURRENT" in column.upper() and "LIAB" in column.upper())
    ]

    print("\n========== CURRENT LIABILITY FIELDS ==========")

    if matching_columns:
        for column in matching_columns:
            print(column)
    else:
        print("No matching current liability fields found.")


if __name__ == "__main__":
    inspect_all_factor_fields(
        stock_code=TEST_STOCK_CODE,
    )

if __name__ == "__main__":
    inspect_current_liability_fields()
