import pandas as pd

print("==============================================")
print("PathSetu - Supply Pre-Positioning Module")
print("==============================================")

# Load village isolation data
input_file = "data/village_isolation.csv"

villages = pd.read_csv(input_file)

print()
print(f"Villages loaded: {len(villages)}")

# Check required columns
required_columns = [
    "village",
    "isolation_score",
    "isolation_level",
    "normal_distance_m",
    "risk_adjusted_distance_m",
    "travel_cost_increase_percent"
]

missing_columns = [
    column
    for column in required_columns
    if column not in villages.columns
]

if missing_columns:
    print()
    print("ERROR: Missing columns:")
    print(missing_columns)
    raise ValueError("Required columns are missing.")

print("Required columns verified.")

# Convert numeric columns
villages["isolation_score"] = pd.to_numeric(
    villages["isolation_score"],
    errors="coerce"
)

villages["travel_cost_increase_percent"] = pd.to_numeric(
    villages["travel_cost_increase_percent"],
    errors="coerce"
)

villages["normal_distance_m"] = pd.to_numeric(
    villages["normal_distance_m"],
    errors="coerce"
)

villages["risk_adjusted_distance_m"] = pd.to_numeric(
    villages["risk_adjusted_distance_m"],
    errors="coerce"
)

villages = villages.dropna(
    subset=[
        "isolation_score",
        "travel_cost_increase_percent"
    ]
)

# Isolation component
villages["isolation_component"] = (
    villages["isolation_score"].clip(0, 100)
)

# Travel disruption component
villages["travel_component"] = (
    villages["travel_cost_increase_percent"].clip(0, 100)
)

# Calculate supply priority score
villages["priority_score"] = (
    0.70 * villages["isolation_component"]
    +
    0.30 * villages["travel_component"]
)

villages["priority_score"] = (
    villages["priority_score"].clip(0, 100)
)

# Priority level
def priority_level(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MODERATE"

    elif score < 75:
        return "HIGH"

    else:
        return "VERY HIGH"


villages["priority_level"] = (
    villages["priority_score"]
    .apply(priority_level)
)

# Recommended supplies
def recommend_supplies(level):

    if level == "VERY HIGH":
        return (
            "Water, packaged food, first-aid supplies, "
            "emergency kits"
        )

    elif level == "HIGH":
        return (
            "Water, packaged food, first-aid supplies"
        )

    elif level == "MODERATE":
        return (
            "Water, packaged food, basic emergency supplies"
        )

    else:
        return "Basic emergency supplies"


villages["recommended_supplies"] = (
    villages["priority_level"]
    .apply(recommend_supplies)
)

# Convert distances from metres to kilometres
villages["normal_distance_km"] = (
    villages["normal_distance_m"] / 1000
)

villages["risk_adjusted_distance_km"] = (
    villages["risk_adjusted_distance_m"] / 1000
)

# Sort highest priority first
villages = villages.sort_values(
    by="priority_score",
    ascending=False
)

# Select final columns
output = villages[
    [
        "village",
        "isolation_score",
        "isolation_level",
        "normal_distance_km",
        "risk_adjusted_distance_km",
        "travel_cost_increase_percent",
        "priority_score",
        "priority_level",
        "recommended_supplies"
    ]
].copy()

# Save output
output_file = "data/supply_priorities.csv"

output.to_csv(
    output_file,
    index=False
)

# Display results
print()
print("Supply prioritization completed.")
print()

print(
    output[
        [
            "village",
            "priority_score",
            "priority_level"
        ]
    ].to_string(index=False)
)

# Summary
print()
print("==============================================")
print("Priority Summary")
print("==============================================")

print(
    output["priority_level"]
    .value_counts()
    .to_string()
)

print()
print(f"Output saved to: {output_file}")

print()
print("==============================================")
print("SUPPLY PRE-POSITIONING COMPLETE")
print("==============================================")