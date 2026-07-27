import pandas as pd
import akshare as ak


def fetch_stock_valuation(
    stock_code: str,
) -> pd.DataFrame:
    pure_stock_code = stock_code[-6:]

    if hasattr(ak, "stock_a_indicator_lg"):
        stock_valuation = ak.stock_a_indicator_lg(
            symbol=pure_stock_code,
        )

    elif hasattr(ak, "stock_a_lg_indicator"):
        stock_valuation = ak.stock_a_lg_indicator(
            symbol=pure_stock_code,
        )

    else:
        raise AttributeError(
            "The Legu valuation interface was not found "
            "in the current AKShare version."
        )

    if stock_valuation.empty:
        raise ValueError(f"No valuation data returned for {stock_code}.")

    stock_valuation.insert(
        0,
        "stock_code",
        stock_code,
    )

    return stock_valuation


stock_valuation = fetch_stock_valuation("sz002067")

print(stock_valuation.columns.tolist())
print(stock_valuation.head())
