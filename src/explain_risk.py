import pandas as pd
import numpy as np

INPUT_FILE = "data/road_risk_dataset.csv"

print("Loading PathSetu risk dataset...")

df = pd.read_csv(INPUT_FILE)

print("Records loaded:", len(df))


# =========================================================
# 1. Prepare rainfall values
# =========================================================

df["rain_24h"] = df["rain_24h"].fillna(0)
df["rain_72h"] = df["rain_72h"].fillna(0)
df["rain_7days"] = df["rain_7days"].fillna(0)


# =========================================================
# 2. Calculate individual risk components
# =========================================================

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


rainfall_score = (
    0.40 * rain_24_score
    + 0.35 * rain_72_score
    + 0.25 * rain_7_score
)


slope_score = np.clip(
    (df["slope_degrees"] - 10) / 35,
    0,
    1
)


distance_score = 1 - np.clip(
    df["distance_to_nearest_landslide_km"] / 10,
    0,
    1
)


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
# 3. Calculate weighted contributions
# =========================================================

df["rainfall_contribution"] = (
    rainfall_score * 40
)

df["slope_contribution"] = (
    slope_score * 25
)

df["landslide_contribution"] = (
    landslide_history_score * 35
)


# =========================================================
# 4. Verify total
# =========================================================

df["calculated_risk"] = (
    df["rainfall_contribution"]
    + df["slope_contribution"]
    + df["landslide_contribution"]
)


# =========================================================
# 5. Generate explanation
# =========================================================

def explain_row(row):

    factors = []

    if row["rainfall_contribution"] >= 20:
        factors.append(
            "heavy recent rainfall"
        )

    elif row["rainfall_contribution"] >= 10:
        factors.append(
            "moderate recent rainfall"
        )

    if row["slope_contribution"] >= 18:
        factors.append(
            "very steep terrain"
        )

    elif row["slope_contribution"] >= 10:
        factors.append(
            "steep terrain"
        )

    if row["landslide_contribution"] >= 25:
        factors.append(
            "strong historical landslide evidence nearby"
        )

    elif row["landslide_contribution"] >= 15:
        factors.append(
            "historical landslide activity nearby"
        )

    elif row["landslide_contribution"] >= 8:
        factors.append(
            "some historical landslide activity nearby"
        )

    if not factors:
        return "Low contribution from rainfall, terrain and landslide history."

    if len(factors) == 1:
        return factors[0].capitalize() + "."

    return (
        ", ".join(factors[:-1]).capitalize()
        + " and "
        + factors[-1]
        + "."
    )


df["risk_explanation"] = df.apply(
    explain_row,
    axis=1
)


# =========================================================
# 6. Select highest-risk records
# =========================================================

highest = (
    df
    .sort_values(
        "calculated_risk",
        ascending=False
    )
    .head(10)
)


# =========================================================
# 7. Display results
# =========================================================

print("\n====================================")
print("EXPLAINABLE RISK ENGINE")
print("====================================")

print("\nTop 10 highest-risk records:\n")

print(
    highest[
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
            "rainfall_contribution",
            "slope_contribution",
            "landslide_contribution",
            "calculated_risk",
            "risk_explanation"
        ]
    ].to_string(index=False)
)


# =========================================================
# 8. Save explanation dataset
# =========================================================

OUTPUT_FILE = "data/road_risk_explained.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nExplanation dataset saved to:")
print(OUTPUT_FILE)

print("\nExplainable risk processing complete!")