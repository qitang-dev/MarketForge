from pathlib import Path
from data_utils import *
import pandas as pd


def summarize_stock_patterns(
    stock_data_patterns: pd.DataFrame,
    stock_code: str,
) -> dict:
    trading_days = len(stock_data_patterns)

    sideways_days = int(stock_data_patterns["sideways_box"].sum())

    violent_fluctuation_days = int(stock_data_patterns["violent_fluctuation"].sum())

    volume_price_surge_days = int(stock_data_patterns["volume_price_surge"].sum())

    sideways_ratio = sideways_days / trading_days if trading_days > 0 else float("nan")

    violent_fluctuation_ratio = (
        violent_fluctuation_days / trading_days if trading_days > 0 else float("nan")
    )

    volume_price_surge_ratio = (
        volume_price_surge_days / trading_days if trading_days > 0 else float("nan")
    )

    average_box_width_20 = stock_data_patterns["box_width_20"].dropna().mean()

    average_abs_ma_20_slope = stock_data_patterns["ma_20_slope"].dropna().abs().mean()

    return {
        "stock_code": stock_code,
        "trading_days": trading_days,
        "sideways_days": sideways_days,
        "sideways_ratio": sideways_ratio,
        "violent_fluctuation_days": violent_fluctuation_days,
        "violent_fluctuation_ratio": violent_fluctuation_ratio,
        "volume_price_surge_days": volume_price_surge_days,
        "volume_price_surge_ratio": volume_price_surge_ratio,
        "average_box_width_20": average_box_width_20,
        "average_abs_ma_20_slope": average_abs_ma_20_slope,
    }


def summarize_all_stock_data_patterns() -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []
    stock_pattern_summaries = []

    project_root_path = Path(__file__).resolve().parent.parent
    stock_data_dir_path = project_root_path / "data"

    try:
        stock_code_list: list[str] = read_stock_code_list(stock_data_dir_path)
    except Exception as error:
        print(f"Failed to read stock code list: {error}")
        return

    stock_data_patterns_dir_path = stock_data_dir_path / "patterns"

    stock_data_analysis_dir_path = stock_data_dir_path / "analysis"

    stock_data_analysis_dir_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    for stock_code in stock_code_list:
        print(f"Start summarizing pattern indicators " f"for {stock_code}...")

        stock_data_patterns_path = (
            stock_data_patterns_dir_path / f"{stock_code}_with_pattern_columns.csv"
        )

        try:
            stock_data_patterns = load_stock_data_from_csv(
                stock_data_patterns_path,
                stock_code,
            )

            stock_pattern_summary = summarize_stock_patterns(
                stock_data_patterns,
                stock_code,
            )

            stock_pattern_summaries.append(stock_pattern_summary)

            print(f"Finished summarizing pattern indicators " f"for {stock_code}")

            success_count += 1

        except Exception as error:
            print(
                f"Failed to summarize pattern indicators " f"for {stock_code}: {error}"
            )

            failed_count += 1
            failed_codes.append(stock_code)

    stock_pattern_summary_data = pd.DataFrame(stock_pattern_summaries)

    if not stock_pattern_summary_data.empty:
        stock_pattern_summary_data = stock_pattern_summary_data.sort_values(
            by=[
                "violent_fluctuation_ratio",
                "volume_price_surge_ratio",
            ],
            ascending=False,
        ).reset_index(drop=True)

    stock_pattern_summary_path = (
        stock_data_analysis_dir_path / "stock_pattern_summary.csv"
    )

    stock_pattern_summary_data.to_csv(
        stock_pattern_summary_path,
        encoding="utf-8",
        index=False,
        float_format="%.6f",
    )

    if failed_count == 0:
        print("\nSuccessfully summarized pattern indicators " "for all stock data.\n")
    else:
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")

    print(f"Summary file saved to: " f"{stock_pattern_summary_path}")


if __name__ == "__main__":
    summarize_all_stock_data_patterns()
