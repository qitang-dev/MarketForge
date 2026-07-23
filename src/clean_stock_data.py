from pathlib import Path
from helper_functions import *
import pandas as pd


def clean_stock_data(
        stock_data: pd.DataFrame,
        required_columns=["open", "close", "high", "low", "amount"],
        date_as_index=True,
        ) -> pd.DataFrame:

    cleaned_stock_data = stock_data.copy()

    cleaned_stock_data.columns = cleaned_stock_data.columns.str.strip()

    cleaned_stock_data["date"] = pd.to_datetime(cleaned_stock_data["date"], errors="coerce")

    numerical_columns = ["open", "close", "high", "low", "amount"]

    for column in numerical_columns:
        cleaned_stock_data[column] = pd.to_numeric(
            cleaned_stock_data[column],
            errors="coerce"
        )

    core_columns = ["date", *required_columns]

    cleaned_stock_data = cleaned_stock_data.dropna(subset=core_columns)
    cleaned_stock_data = cleaned_stock_data.drop_duplicates(subset=["date"], keep="last")
    cleaned_stock_data = cleaned_stock_data.sort_values("date", ascending=True).reset_index(drop=True)

    if date_as_index: 
        cleaned_stock_data = cleaned_stock_data.set_index("date")

    return cleaned_stock_data

    
def load_all_cleaned_stock_data() -> None:
    project_root_path = Path(__file__).parent.parent
    stock_code_list_path = project_root_path / "data" / "stock_code_list.csv"
    success_count  = 0
    failed_count = 0
    failed_codes = []
    try:
        stock_code_list_df = pd.read_csv(
            stock_code_list_path,
            header=None,
            names=["stock_code"]
            )
    except FileExistsError as error:
        print(f"No such file 'stock_code_list.csv' in {stock_code_list} : {error}")
        return

    stock_code_list = stock_code_list_df["stock_code"].tolist()

    stock_data_dir_path = project_root_path / "data"
    cleaned_data_dir_path = stock_data_dir_path / "cleaned_unadjusted"
    cleaned_data_dir_path.mkdir(parents=True, exist_ok=True)

    for stock_code in stock_code_list:
        print(f"\nstart cleaning {stock_code}...")

        try:
            raw_stock_data_path = stock_data_dir_path / "raw_unadjusted" / f"{stock_code}_daily_unadjusted_tx.csv"
            raw_stock_data = load_stock_data_from_csv(raw_stock_data_path, stock_code)
            cleaned_stock_data = clean_stock_data(raw_stock_data, ["open", "close", "high", "low", "amount"], False)
            cleaned_stock_data_path = stock_data_dir_path / "cleaned_unadjusted" / f"cleaned_{stock_code}_daily_unadjusted_tx.csv"
            cleaned_stock_data.to_csv(cleaned_stock_data_path, encoding='utf-8')
            success_count += 1
            
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
    load_all_cleaned_stock_data()


