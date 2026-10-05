import pandas as pd

input_file = "data/historical_weather.csv"
output_file = "data/weather_features.csv"

print("Loading historical weather data...")

df = pd.read_csv(input_file)

df["date"] = pd.to_datetime(df["date"])

df = df.sort_values("date")

df["rain_24h"] = df["rain"].rolling(1).sum()

df["rain_72h"] = df["rain"].rolling(3).sum()

df["rain_7days"] = df["rain"].rolling(7).sum()

df.to_csv(output_file, index=False)

print("Weather features created successfully!")

print("\nLatest weather features:")
print(df.tail(10))

print(f"\nTotal records: {len(df)}")