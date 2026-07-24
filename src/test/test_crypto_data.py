import akshare as ak

crypto_data = ak.crypto_js_spot()

print(crypto_data["交易品种"].astype(str).tolist())

eth_data = crypto_data.loc[
    crypto_data["交易品种"].astype(str).str.upper().str.contains("ETH", na=False)
]

print(eth_data)
