from pathlib import Path
import json
import re

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STOCK_MINUTE_CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "minute" / "cleaned"

WEBSITE_DATA_DIR = PROJECT_ROOT / "website" / "data"

FILE_NAME_PATTERN = re.compile(
    r"cleaned_"
    r"(?P<stock_code>(?:sh|sz)\d{6})"
    r"_5min_"
    r"(?P<adjust_name>qfq|unadjusted)"
    r"_baostock\.csv"
)


def prepare_single_kline_web_data(
    input_file_path: Path,
    output_file_path: Path,
) -> int:
    stock_data = pd.read_csv(
        input_file_path,
        parse_dates=["datetime"],
    )

    required_columns = [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    missing_columns = [
        column for column in required_columns if column not in stock_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in "
            f"{input_file_path.name}: "
            f"{missing_columns}."
        )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for column in numeric_columns:
        stock_data[column] = pd.to_numeric(
            stock_data[column],
            errors="coerce",
        )

    stock_data = (
        stock_data.dropna(subset=required_columns)
        .drop_duplicates(
            subset=["datetime"],
            keep="last",
        )
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    web_data = stock_data[required_columns].copy()

    web_data["time"] = (
        web_data["datetime"].to_numpy(dtype="datetime64[s]").astype("int64")
    )

    web_data = web_data[
        [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ]

    output_file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    web_data.to_json(
        output_file_path,
        orient="records",
        force_ascii=False,
        double_precision=10,
    )

    return len(web_data)


def prepare_all_kline_web_data() -> None:
    manifest_data: dict[str, dict] = {}

    for adjust_name in [
        "qfq",
        "unadjusted",
    ]:
        input_dir_path = STOCK_MINUTE_CLEANED_DATA_DIR / adjust_name

        input_file_paths = sorted(input_dir_path.glob("*.csv"))

        for input_file_path in input_file_paths:
            matched_result = FILE_NAME_PATTERN.fullmatch(input_file_path.name)

            if matched_result is None:
                print("[SKIPPED] Unrecognized file name: " f"{input_file_path.name}")
                continue

            stock_code = matched_result.group("stock_code")

            file_adjust_name = matched_result.group("adjust_name")

            output_file_name = f"{stock_code}_5min_" f"{file_adjust_name}.json"

            output_file_path = WEBSITE_DATA_DIR / file_adjust_name / output_file_name

            try:
                row_count = prepare_single_kline_web_data(
                    input_file_path,
                    output_file_path,
                )

                if stock_code not in manifest_data:
                    manifest_data[stock_code] = {
                        "code": stock_code,
                        "files": {},
                    }

                relative_file_path = output_file_path.relative_to(
                    PROJECT_ROOT / "website"
                )

                manifest_data[stock_code]["files"][
                    file_adjust_name
                ] = f"./{relative_file_path.as_posix()}"

                print(
                    f"[SUCCESS] {stock_code} "
                    f"{file_adjust_name}: "
                    f"{row_count} rows."
                )

            except Exception as error:
                print(f"[FAILED] {input_file_path.name}: " f"{error}")

    stock_list = [manifest_data[stock_code] for stock_code in sorted(manifest_data)]

    manifest_file_path = WEBSITE_DATA_DIR / "manifest.json"

    manifest_file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with manifest_file_path.open(
        "w",
        encoding="utf-8",
    ) as manifest_file:
        json.dump(
            {
                "frequency": "5min",
                "source": "BaoStock",
                "stocks": stock_list,
            },
            manifest_file,
            ensure_ascii=False,
            indent=4,
        )

    print("\n[SUCCESS] Generated web data for " f"{len(stock_list)} stocks.")

    print(f"[SUCCESS] Manifest stored at " f"{manifest_file_path}.")


if __name__ == "__main__":
    prepare_all_kline_web_data()
