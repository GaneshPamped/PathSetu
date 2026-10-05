import requests
import csv
from datetime import datetime

LATITUDE = 27.3314
LONGITUDE = 88.6138

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code",
    "hourly": "precipitation,rain",
    "forecast_days": 3,
    "timezone": "Asia/Kolkata"
}

print("Fetching weather data for Gangtok...")

response = requests.get(url, params=params)

if response.status_code == 200:

    data = response.json()
    current = data["current"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "timestamp": timestamp,
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "rain": current["rain"],
        "weather_code": current["weather_code"]
    }

    file_path = "data/weather.csv"

    file_exists = False

    try:
        with open(file_path, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(file_path, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=row.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    print("\nWeather successfully saved!")
    print(row)

else:
    print("Weather request failed.")
    print("Status:", response.status_code)