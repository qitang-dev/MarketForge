from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

project_root_path = Path(__file__).resolve().parent.parent

stock_data_dir_path = project_root_path / "data"
input_dir_path = project_root_path / "data" / "cleaned_unadjusted"
output_dir_path = project_root_path / "data" / "analysis" / "limit_analysis"


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
        result.dropna(subset=["date", "open", "high", "low", "close"])
        .drop_duplicates(subset=["date"], keep="last")
        .sort_values("date")
        .reset_index(drop=True)
    )

    limit_rate = get_limit_rate(stock_code)

    result["previous_close"] = result["close"].shift(1)

    result["limit_up_price"] = result["previous_close"] * (1 + limit_rate)

    result["limit_down_price"] = result["previous_close"] * (1 - limit_rate)

    result["limit_up"] = result["close"] >= result["limit_up_price"]

    result["limit_down"] = result["close"] <= result["limit_down_price"]

    result["next_open_return"] = result["open"].shift(-1) / result["close"] - 1

    end_date = result["date"].max()
    start_date = end_date - pd.DateOffset(years=1)

    recent_data = result.loc[result["date"] >= start_date].copy()

    limit_up_data = recent_data.loc[recent_data["limit_up"]]

    summary = {
        "stock_code": stock_code,
        "limit_up_days": int(recent_data["limit_up"].sum()),
        "limit_down_days": int(recent_data["limit_down"].sum()),
        "average_next_open_return": (limit_up_data["next_open_return"].mean()),
        "next_open_up_ratio": ((limit_up_data["next_open_return"] > 0).mean()),
    }

    return result, summary


def process_all_stocks() -> None:
    output_dir_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    daily_output_dir_path = output_dir_path / "daily"
    daily_output_dir_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    summaries = []
    try:
        stock_code_list = read_stock_code_list(stock_data_dir_path)
    except RuntimeError as error:
        print(f"Failed to read stock code list: {error}")
        return

    for stock_code in stock_code_list:

        try:
            stock_data_path = (
                input_dir_path / f"cleaned_{stock_code}_daily_unadjusted_tx.csv"
            )
            stock_data = pd.read_csv(stock_data_path)

            analyzed_data, summary = analyze_price_limit(
                stock_data,
                stock_code,
            )

            summaries.append(summary)

            analyzed_data.to_csv(
                daily_output_dir_path / f"{stock_code}_limit_analysis.csv",
                index=False,
                encoding="utf-8-sig",
                float_format="%.4f",
            )

            print(f"[SUCCESS] Price-limit analysis completed: {stock_code}")

        except Exception as error:
            print(f"[FAILED] {stock_code}: {error}")

    summary_data = pd.DataFrame(summaries)

    summary_data.to_csv(
        output_dir_path / "limit_summary.csv",
        index=False,
        encoding="utf-8-sig",
        float_format="%.4f",
    )

    print("Price-limit analysis completed for all stock datasets.")


if __name__ == "__main__":
    process_all_stocks()
