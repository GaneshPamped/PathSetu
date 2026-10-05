import requests
import pandas as pd

LATITUDE = 27.3314
LONGITUDE = 88.6138

START_DATE = "2023-01-01"
END_DATE = "2025-12-31"

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "daily": "precipitation_sum,rain_sum",
    "timezone": "Asia/Kolkata"
}

print("Downloading historical weather...")

response = requests.get(url, params=params)

if response.status_code == 200:

    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "precipitation": data["daily"]["precipitation_sum"],
        "rain": data["daily"]["rain_sum"]
    })

    df.to_csv(
        "data/historical_weather.csv",
        index=False
    )

    print("Historical weather saved.")
    print(df.head())

    print(f"\nTotal records: {len(df)}")

else:

    print("Request failed.")
    print("Status code:", response.status_code)