"""
binance_klines
Endpoint: GET https://fapi.binance.com/fapi/v1/klines
Docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
"""
import requests

BASE_URL = "https://fapi.binance.com"
ENDPOINT = "/fapi/v1/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 1

# Mapping of Kline fields to their meanings and expected types
FIELDS = [
    ("Open time", int),
    ("Open price", str),
    ("High price", str),
    ("Low price", str),
    ("Close price", str),
    ("Volume", str),
    ("Close time", int),
    ("Quote asset volume", str),
    ("Number of trades", int),
    ("Taker buy base asset volume", str),
    ("Taker buy quote asset volume", str),
    ("Ignore", str),
]

if __name__ == "__main__":
    response = requests.get(
        BASE_URL + ENDPOINT,
        params={
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "limit": LIMIT
        },
    )
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        print("Error:", response.text)
    else:
        klines = response.json()
        kline = klines[0]
        print(f"\nKline data for {SYMBOL} ({INTERVAL}):\n")
        for (name, dtype), value in zip(FIELDS, kline):
            # Assert type correctness
            assert isinstance(value, dtype), (
                f"Type mismatch for '{name}': "
                f"expected {dtype.__name__}, got {type(value).__name__}")
            print(f"{name:<35} ({dtype.__name__}): {value}")
"""
Output:
Status Code: 200

Kline data for BTCUSDT (1m):

Open time                           (int): 1754817420000
Open price                          (str): 118359.50
High price                          (str): 118359.50
Low price                           (str): 118300.00
Close price                         (str): 118300.00
Volume                              (str): 93.114
Close time                          (int): 1754817479999
Quote asset volume                  (str): 11017878.82960
Number of trades                    (int): 1301
Taker buy base asset volume         (str): 6.442
Taker buy quote asset volume        (str): 762140.16380
Ignore                              (str): 0
"""
