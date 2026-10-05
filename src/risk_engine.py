import pandas as pd
import numpy as np

INPUT_FILE = "data/pathsetu_dataset.csv"
OUTPUT_FILE = "data/road_risk_dataset.csv"

print("Loading PathSetu master dataset...")

df = pd.read_csv(INPUT_FILE)

print("Records loaded:", len(df))


# =========================================================
# 1. Handle missing rainfall values
# =========================================================

print("\nHandling rainfall values...")

df["rain_24h"] = df["rain_24h"].fillna(0)

df["rain_72h"] = df["rain_72h"].fillna(0)

df["rain_7days"] = df["rain_7days"].fillna(0)


# =========================================================
# 2. Normalize rainfall
# =========================================================

print("Calculating rainfall risk...")

# These thresholds are prototype thresholds.
# They can later be calibrated using real historical
# disruption/landslide observations.

rain_24_score = np.clip(
    df["rain_24h"] / 100,
    0,
    1
)

rain_72_score = np.clip(
    df["rain_72h"] / 200,
    0,
    1
)

rain_7_score = np.clip(
    df["rain_7days"] / 300,
    0,
    1
)


# Combine rainfall indicators

rainfall_score = (
    0.40 * rain_24_score
    + 0.35 * rain_72_score
    + 0.25 * rain_7_score
)


# =========================================================
# 3. Slope risk
# =========================================================

print("Calculating slope risk...")

slope_score = np.clip(
    (df["slope_degrees"] - 10) / 35,
    0,
    1
)


# =========================================================
# 4. Landslide proximity risk
# =========================================================

print("Calculating landslide proximity risk...")

distance_score = 1 - np.clip(
    df["distance_to_nearest_landslide_km"] / 10,
    0,
    1
)


# =========================================================
# 5. Nearby landslide risk
# =========================================================

print("Calculating nearby landslide risk...")

landslide_1km_score = np.clip(
    df["landslides_within_1km"] / 5,
    0,
    1
)

landslide_5km_score = np.clip(
    df["landslides_within_5km"] / 20,
    0,
    1
)


landslide_history_score = (
    0.50 * distance_score
    + 0.30 * landslide_1km_score
    + 0.20 * landslide_5km_score
)


# =========================================================
# 6. Final risk score
# =========================================================

print("Calculating final risk score...")


risk_score = (
    0.40 * rainfall_score
    + 0.25 * slope_score
    + 0.35 * landslide_history_score
)


# Convert to 0–100

df["risk_score"] = (
    risk_score * 100
)


# =========================================================
# 7. Risk category
# =========================================================

def classify_risk(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MODERATE"

    elif score < 75:
        return "HIGH"

    else:
        return "VERY HIGH"


df["risk_level"] = df["risk_score"].apply(
    classify_risk
)


# =========================================================
# 8. Save
# =========================================================

print("\nSaving risk dataset...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 9. Results
# =========================================================

print("\n====================================")
print("PATHSETU RISK ENGINE COMPLETE")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nRisk score statistics:")

print(
    "Minimum:",
    round(df["risk_score"].min(), 2)
)

print(
    "Maximum:",
    round(df["risk_score"].max(), 2)
)

print(
    "Average:",
    round(df["risk_score"].mean(), 2)
)

print("\nRisk level distribution:")

print(
    df["risk_level"].value_counts()
)

print("\nHighest-risk records:")

print(
    df[
        [
            "road_u",
            "road_v",
            "date",
            "rain_24h",
            "rain_72h",
            "rain_7days",
            "slope_degrees",
            "distance_to_nearest_landslide_km",
            "landslides_within_1km",
            "risk_score",
            "risk_level"
        ]
    ]
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)