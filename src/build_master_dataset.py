import pandas as pd

ROAD_FILE = "data/road_landslide_features.csv"
WEATHER_FILE = "data/weather_features.csv"

OUTPUT_FILE = "data/pathsetu_dataset.csv"

print("Loading road and landslide features...")

roads = pd.read_csv(ROAD_FILE)

print("Road records:", len(roads))

print("\nLoading historical weather features...")

weather = pd.read_csv(WEATHER_FILE)

print("Weather records:", len(weather))


# ---------------------------------------------------------
# Prepare date column
# ---------------------------------------------------------

weather["date"] = pd.to_datetime(
    weather["date"]
)


# ---------------------------------------------------------
# Create combination of every road and every weather day
# ---------------------------------------------------------

print("\nCombining road data with historical weather...")

roads["_key"] = 1
weather["_key"] = 1

master = roads.merge(
    weather,
    on="_key",
    how="outer"
)

# Remove temporary key
master = master.drop(
    columns=["_key"]
)


# ---------------------------------------------------------
# Save master dataset
# ---------------------------------------------------------

print("\nSaving master dataset...")

master.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

print("\n====================================")
print("MASTER DATASET CREATED")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nTotal records:")
print(len(master))

print("\nTotal columns:")
print(len(master.columns))

print("\nRoad segments represented:")
print(master["road_u"].nunique())

print("\nWeather dates represented:")
print(master["date"].nunique())

print("\nColumns:")
print(list(master.columns))

print("\nFirst 5 records:")
print(master.head())