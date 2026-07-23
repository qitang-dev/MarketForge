from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = PROJECT_ROOT / "data" / "cleaned_unadjusted"
OUTPUT_DIR = PROJECT_ROOT / "data" / "analysis" / "limit_analysis"


def get_limit_rate(stock_code: str) -> float:
    
    pure_code = stock_code[-6:]

    if pure_code.startswith(("300", "301", "688")):
        return 0.20

    return 0.10


def analyze_price_limit(
    stock_data: pd.DataFrame,
    stock_code: str,
) -> tuple[pd.DataFrame, dict]:
    result = stock_data.copy()

    result["date"] = pd.to_datetime(
        result["date"],
        errors="coerce",
    )

    result = (
        result
        .dropna(subset=["date", "open", "high", "low", "close"])
        .drop_duplicates(subset=["date"], keep="last")
        .sort_values("date")
        .reset_index(drop=True)
    )

    limit_rate = get_limit_rate(stock_code)

    result["previous_close"] = result["close"].shift(1)

    result["limit_up_price"] = (
        result["previous_close"] * (1 + limit_rate)
    ).round(2)

    result["limit_down_price"] = (
        result["previous_close"] * (1 - limit_rate)
    ).round(2)

    result["limit_up"] = (
        result["close"] >= result["limit_up_price"]
    )

    result["limit_down"] = (
        result["close"] <= result["limit_down_price"]
    )

    result["next_open_return"] = (
        result["open"].shift(-1)
        / result["close"]
        - 1
    )

    end_date = result["date"].max()
    start_date = end_date - pd.DateOffset(years=1)

    recent_data = result.loc[
        result["date"] >= start_date
    ].copy()

    limit_up_data = recent_data.loc[
        recent_data["limit_up"]
    ]

    summary = {
        "stock_code": stock_code,
        "limit_up_days": int(
            recent_data["limit_up"].sum()
        ),
        "limit_down_days": int(
            recent_data["limit_down"].sum()
        ),
        "average_next_open_return": (
            limit_up_data["next_open_return"].mean()
        ),
        "next_open_up_ratio": (
            (
                limit_up_data["next_open_return"] > 0
            ).mean()
        ),
    }

    return result, summary


def process_all_stocks() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily_output_dir = OUTPUT_DIR / "daily"
    daily_output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summaries = []

    for file_path in INPUT_DIR.glob("*.csv"):
        stock_code = file_path.stem.split("_")[1]

        try:
            stock_data = pd.read_csv(file_path)

            analyzed_data, summary = analyze_price_limit(
                stock_data,
                stock_code,
            )

            summaries.append(summary)

            analyzed_data.to_csv(
                daily_output_dir
                / f"{stock_code}_limit_analysis.csv",
                index=False,
                encoding="utf-8-sig",
                float_format="%.6f",
            )

            print(
                f"[SUCCESS] Price-limit analysis completed: "
                f"{stock_code}"
            )

        except Exception as error:
            print(
                f"[FAILED] {stock_code}: {error}"
            )

    summary_data = pd.DataFrame(summaries)

    summary_data.to_csv(
        OUTPUT_DIR / "limit_summary.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.6f",
    )

    print(
        "Price-limit analysis completed for all stock datasets."
    )


if __name__ == "__main__":
    process_all_stocks()