"""
binance_time
Endpoint: GET https://fapi.binance.com/fapi/v1/time
Docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Check-Server-Time
"""

from datetime import datetime
from datetime import timezone

import requests

BASE_URL = "https://fapi.binance.com"
ENDPOINT = "/fapi/v1/time"

# Expected fields and their types
FIELDS = [("serverTime", int)]

if __name__ == "__main__":
    response = requests.get(BASE_URL + ENDPOINT)
    print("Status Code:", response.status_code)

    if response.status_code != 200:
        print("Error:", response.text)
    else:
        data = response.json()
        print("\nCheck Server Time Response:\n")
        for name, dtype in FIELDS:
            value = data.get(name)
            assert isinstance(value, dtype), (
                f"Type mismatch for '{name}': expected {dtype.__name__}, "
                f"got {type(value).__name__}")
            # Convert to human-readable UTC time
            human_time = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
            print(
                f"{name:<15} ({dtype.__name__}): {value}  ->  {human_time} UTC"
            )
"""
Output:
Status Code: 200

Check Server Time Response:

serverTime      (int): 1754817511316  ->  2025-08-10 09:18:31.316000+00:00 UTC
"""
