from pathlib import Path
import pandas as pd


def read_stock_code_list(
    stock_data_dir_path: Path,
    file_name="baostock_code_list.csv",
) -> list[str]:

    try:
        stock_code_list_path = stock_data_dir_path / file_name

        stock_code_list_df = pd.read_csv(
            stock_code_list_path,
            header=None,
            names=["stock_code"],
        )

        stock_code_list = stock_code_list_df["stock_code"].tolist()

    except Exception as error:
        raise RuntimeError(f"failed to read {file_name} : {error}") from error

    return stock_code_list


def convert_to_baostock_code(stock_code: str) -> str:
    normalized_code = stock_code.strip().lower()

    if "." in normalized_code:
        return normalized_code

    if normalized_code.startswith(("sh", "sz")):
        return f"{normalized_code[:2]}.{normalized_code[2:]}"

    raise ValueError("Invalid Stock Code Format.")
