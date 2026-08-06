from pathlib import Path
import pandas as pd


def read_stock_code_list(
    stock_data_dir_path: Path,
    file_name="stock_code_list.csv",
) -> list[str]:

    stock_code_list_path = stock_data_dir_path / file_name

    try:
        stock_code_list_df = pd.read_csv(
            stock_code_list_path,
            header=None,
            names=["stock_code"],
        )
    except Exception as error:
        raise RuntimeError(
            f"No such file {[file_name]} in the path {stock_code_list_path} : {error}"
        ) from error

    stock_code_list = (
        stock_code_list_df["stock_code"].dropna().astype(str).str.strip().tolist()
    )

    return stock_code_list
