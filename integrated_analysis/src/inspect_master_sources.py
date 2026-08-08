import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


fundamental_path = (
    PROJECT_ROOT
    / "fundamentals"
    / "data"
    / "factors"
    / "a_share"
    / "a_share_fundamental_factors.csv"
)

valuation_path = (
    PROJECT_ROOT
    / "market_data_pipeline"
    / "data"
    / "cleaned"
    / "valuation"
    / "a_share_valuation.csv"
)


fundamental_data = pd.read_csv(
    fundamental_path,
    encoding="utf-8-sig",
)

valuation_data = pd.read_csv(
    valuation_path,
    encoding="utf-8-sig",
)


print("\n========== FUNDAMENTAL ==========")

print(fundamental_data.columns.tolist())

print(fundamental_data.head())

print(fundamental_data.shape)


print("\n========== VALUATION ==========")

print(valuation_data.columns.tolist())

print(valuation_data.head())

print(valuation_data.shape)
