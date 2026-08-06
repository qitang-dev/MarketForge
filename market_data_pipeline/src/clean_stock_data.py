from pathlib import Path
from data_utils import read_stock_code_list
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STOCK_DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCK_DATA_DIR = STOCK_DATA_DIR / "raw"


def clean_stock_data(
    stock_data: pd.DataFrame,
    required_columns=["open", "close", "high", "low", "amount"],
    date_as_index=True,
) -> pd.DataFrame:

    cleaned_stock_data = stock_data.copy()

    cleaned_stock_data.columns = cleaned_stock_data.columns.str.strip()

    cleaned_stock_data["date"] = pd.to_datetime(
        cleaned_stock_data["date"], errors="coerce"
    )

    numerical_columns = ["open", "close", "high", "low", "amount"]

    for column in numerical_columns:
        cleaned_stock_data[column] = pd.to_numeric(
            cleaned_stock_data[column], errors="coerce"
        )

    core_columns = ["date", *required_columns]

    cleaned_stock_data = cleaned_stock_data.dropna(subset=core_columns)
    cleaned_stock_data = cleaned_stock_data.drop_duplicates(
        subset=["date"], keep="last"
    )
    cleaned_stock_data = cleaned_stock_data.sort_values(
        "date", ascending=True
    ).reset_index(drop=True)

    if date_as_index:
        cleaned_stock_data = cleaned_stock_data.set_index("date")

    return cleaned_stock_data


def clean_all_stock_data(adjust_flag: str) -> None:
    success_count = 0
    failed_count = 0
    failed_codes = []

    try:
        stock_code_list: list[str] = read_stock_code_list(STOCK_DATA_DIR)
    except RuntimeError as error:
        print(f"[FAILED] unable to read the stock code list : {error}")
        return

    try:
        cleaned_data_dir_path = STOCK_DATA_DIR / "cleaned" / f"{adjust_flag}"
        cleaned_data_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        print(f"[FAILED] unable to created the directory : {error}")
        return

    for stock_code in stock_code_list:
        print(f"\nStart cleaning {stock_code}...")

        try:

            input_dir_path = RAW_STOCK_DATA_DIR / f"{adjust_flag}"
            input_file_path = (
                input_dir_path / f"{stock_code}_daily_{adjust_flag}_tx.csv"
            )

            raw_stock_data = pd.read_csv(input_file_path, encoding="utf-8")

            cleaned_stock_data = clean_stock_data(
                raw_stock_data, ["open", "close", "high", "low", "amount"], True
            )

            cleaned_stock_data_file_path = (
                cleaned_data_dir_path
                / f"cleaned_{stock_code}_daily_{adjust_flag}_tx.csv"
            )

            cleaned_stock_data.to_csv(cleaned_stock_data_file_path, encoding="utf-8")
            success_count += 1
            print(f"\nFinished cleaning {stock_code}.")

        except Exception as error:
            print(f"faile to clean {stock_code} : {error}")
            failed_count += 1
            failed_codes.append(stock_code)

        print(f"the head of original stock data:\n{raw_stock_data.head()}")
        print(f"\nthe head of cleaned stock data:\n{cleaned_stock_data.head()}")
        print(f"\nthe shape of original stock data: {raw_stock_data.shape}")
        print(f"the shape of cleaned stock data: {cleaned_stock_data.shape}")

        print(f"\nSuccessfully cleaned {stock_code}.\n")

    if failed_count == 0:
        print("\nAll raw stock data is cleaned successfully.\n")
    else:
        print(f"{failed_count} raw stock data is failed to clean.")
        print(f"Success Count: {success_count}")
        print(f"Failed Count: {failed_count}")
        print(f"Failed Code(s): {failed_codes}")


if __name__ == "__main__":
    clean_all_stock_data("qfq")
    clean_all_stock_data("unadjusted")
