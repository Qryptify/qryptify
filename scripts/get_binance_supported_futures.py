import requests

url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
response = requests.get(url)
data = response.json()

symbols = [
    s["symbol"] for s in data["symbols"] if s["contractType"] == "PERPETUAL"
]
print(f"TOTAL {len(symbols)} PAIRS")
print(symbols[:20])
