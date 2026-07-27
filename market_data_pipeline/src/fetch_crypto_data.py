from pathlib import Path

import akshare as ak
import pandas as pd


def fetch_crypto_data(
    crypto_symbol: str,
) -> pd.DataFrame:

    try:
        crypto_data: pd.DataFrame = ak.crypto_js_spot()

    except Exception as error:
        raise RuntimeError(f"Failed to fetch {crypto_symbol}: {error}.") from error

    if crypto_data.empty:
        raise ValueError("Empty crypto data returned.")

    print(f"Returned columns: " f"{crypto_data.columns.tolist()}")

    return crypto_data


def filter_crypto_data(
    crypto_data: pd.DataFrame,
    crypto_symbol: str,
) -> pd.DataFrame:

    possible_symbol_columns = [
        "交易品种",
        "交易对",
        "代码",
        "symbol",
        "Symbol",
        "名称",
    ]

    symbol_column = None

    for column in possible_symbol_columns:
        if column in crypto_data.columns:
            symbol_column = column
            break

    if symbol_column is None:
        raise ValueError("No recognizable crypto symbol column found.")

    symbol_data = (
        crypto_data[symbol_column]
        .astype(str)
        .str.upper()
        .str.replace(
            "/",
            "",
            regex=False,
        )
        .str.replace(
            "-",
            "",
            regex=False,
        )
    )

    pure_crypto_symbol = crypto_symbol.upper().replace("/", "").replace("-", "")

    filtered_crypto_data = crypto_data.loc[
        symbol_data.str.contains(
            pure_crypto_symbol,
            na=False,
        )
    ].copy()

    if filtered_crypto_data.empty:
        raise ValueError(f"No crypto data matched " f"{crypto_symbol}.")

    return filtered_crypto_data


def store_crypto_data(
    crypto_data: pd.DataFrame,
    crypto_symbol: str,
) -> None:

    project_root_path = Path(__file__).resolve().parent.parent

    output_dir_path = project_root_path / "data" / "crypto"

    output_dir_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir_path / f"{crypto_symbol.lower()}_spot.csv"

    crypto_data.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Stored {crypto_symbol} " f"at {output_path}.")


def fetch_all_crypto_data() -> None:
    fetch_results = []

    crypto_symbol_list = [
        "BTCUSD",
    ]

    for crypto_symbol in crypto_symbol_list:
        print(f"Processing: {crypto_symbol}")

        try:
            all_crypto_data = fetch_crypto_data(crypto_symbol)

            crypto_data = filter_crypto_data(
                all_crypto_data,
                crypto_symbol,
            )

            store_crypto_data(
                crypto_data,
                crypto_symbol,
            )

            fetch_results.append(
                {
                    "crypto_symbol": crypto_symbol,
                    "status": "success",
                    "rows": len(crypto_data),
                    "error": None,
                }
            )

        except Exception as error:
            fetch_results.append(
                {
                    "crypto_symbol": crypto_symbol,
                    "status": "failed",
                    "rows": 0,
                    "error": str(error),
                }
            )

    fetch_results_df = pd.DataFrame(
        fetch_results,
        columns=[
            "crypto_symbol",
            "status",
            "rows",
            "error",
        ],
    )

    result_status = fetch_results_df["status"].value_counts()

    success_count = result_status.get(
        "success",
        0,
    )

    failed_count = result_status.get(
        "failed",
        0,
    )

    print(fetch_results_df)
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")


if __name__ == "__main__":
    fetch_all_crypto_data()
