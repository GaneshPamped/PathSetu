import osmnx as ox
import pandas as pd
import networkx as nx
import numpy as np


ROAD_FILE = "data/gangtok_roads.graphml"
VILLAGE_FILE = "data/villages_connected.csv"
RISK_FILE = "data/road_risk_dataset.csv"

OUTPUT_FILE = "data/village_isolation.csv"


# =========================================================
# 1. LOAD ROAD NETWORK
# =========================================================

print("Loading road network...")

graph = ox.load_graphml(
    ROAD_FILE
)

print("Road nodes:", len(graph.nodes))
print("Road edges:", len(graph.edges))


# =========================================================
# 2. LOAD VILLAGES
# =========================================================

print("\nLoading connected villages...")

villages = pd.read_csv(
    VILLAGE_FILE
)

print("Villages:", len(villages))


# =========================================================
# 3. LOAD RISK DATA
# =========================================================

print("\nLoading road risk data...")

risk = pd.read_csv(
    RISK_FILE,
    usecols=[
        "road_u",
        "road_v",
        "road_key",
        "date",
        "risk_score"
    ]
)

print("Risk records:", len(risk))


# =========================================================
# 4. USE MOST RECENT RISK DATE
# =========================================================

print("\nSelecting latest risk conditions...")

risk["date"] = pd.to_datetime(
    risk["date"]
)

latest_date = risk["date"].max()

print("Latest risk date:", latest_date.date())


latest_risk = risk[
    risk["date"] == latest_date
].copy()

print(
    "Road risk records for latest date:",
    len(latest_risk)
)


# =========================================================
# 5. CREATE RISK LOOKUP
# =========================================================

print("\nCreating road risk lookup...")

risk_lookup = {}

for _, row in latest_risk.iterrows():

    key = (
        int(row["road_u"]),
        int(row["road_v"]),
        int(row["road_key"])
    )

    risk_lookup[key] = float(
        row["risk_score"]
    )


print(
    "Risk values available:",
    len(risk_lookup)
)


# =========================================================
# 6. ATTACH RISK TO ROAD NETWORK
# =========================================================

print("\nAttaching risk to road network...")

matched = 0
unmatched = 0


for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    lookup_key = (
        int(u),
        int(v),
        int(key)
    )

    if lookup_key in risk_lookup:

        risk_value = risk_lookup[
            lookup_key
        ]

        matched += 1

    else:

        risk_value = 0.0

        unmatched += 1

    # Make absolutely sure risk is valid
    if not np.isfinite(risk_value):

        risk_value = 0.0

    # Keep risk between 0 and 100
    risk_value = np.clip(
        risk_value,
        0,
        100
    )

    data["risk_score"] = float(
        risk_value
    )


print(
    "Edges matched with risk:",
    matched
)

print(
    "Edges without risk:",
    unmatched
)


# =========================================================
# 7. CREATE SAFE ROUTE WEIGHTS
# =========================================================

print("\nCreating safe route weights...")


for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    # Get road length
    length = data.get(
        "length",
        1
    )

    try:

        length = float(length)

    except:

        length = 1.0


    # Make sure length is valid
    if (
        not np.isfinite(length)
        or length <= 0
    ):

        length = 1.0


    # Get risk
    risk_value = data.get(
        "risk_score",
        0
    )

    try:

        risk_value = float(
            risk_value
        )

    except:

        risk_value = 0.0


    if not np.isfinite(risk_value):

        risk_value = 0.0


    risk_value = np.clip(
        risk_value,
        0,
        100
    )


    # Normal distance
    data["normal_cost"] = length


    # Risk-adjusted distance
    data["risk_cost"] = (
        length
        * (
            1
            + risk_value / 100
        )
    )


# =========================================================
# 8. VERIFY ROUTE WEIGHTS
# =========================================================

print("\nChecking route weights...")

negative_weights = 0
invalid_weights = 0


for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    normal_cost = data[
        "normal_cost"
    ]

    risk_cost = data[
        "risk_cost"
    ]


    if normal_cost < 0:
        negative_weights += 1

    if risk_cost < 0:
        negative_weights += 1


    if (
        not np.isfinite(normal_cost)
        or not np.isfinite(risk_cost)
    ):

        invalid_weights += 1


print(
    "Negative weights:",
    negative_weights
)

print(
    "Invalid weights:",
    invalid_weights
)


# =========================================================
# 9. FIND GANGTOK REFERENCE NODE
# =========================================================

print("\nFinding Gangtok reference point...")

GANGTOK_LAT = 27.3314
GANGTOK_LON = 88.6138


gangtok_node = ox.distance.nearest_nodes(
    graph,
    X=GANGTOK_LON,
    Y=GANGTOK_LAT
)


print(
    "Gangtok road node:",
    gangtok_node
)


# =========================================================
# 10. CALCULATE VILLAGE ACCESSIBILITY
# =========================================================

results = []


print("\nCalculating village accessibility...")


for _, village in villages.iterrows():

    village_name = village[
        "village"
    ]

    village_node = int(
        village[
            "nearest_node"
        ]
    )


    print(
        "Processing:",
        village_name
    )


    # -----------------------------------------------------
    # Normal route
    # -----------------------------------------------------

    try:

        normal_distance = (
            nx.shortest_path_length(
                graph,
                village_node,
                gangtok_node,
                weight="normal_cost"
            )
        )

    except nx.NetworkXNoPath:

        normal_distance = np.nan


    # -----------------------------------------------------
    # Risk-adjusted route
    # -----------------------------------------------------

    try:

        risk_distance = (
            nx.shortest_path_length(
                graph,
                village_node,
                gangtok_node,
                weight="risk_cost"
            )
        )

    except nx.NetworkXNoPath:

        risk_distance = np.nan


    # -----------------------------------------------------
    # Travel cost increase
    # -----------------------------------------------------

    if (
        pd.notna(normal_distance)
        and normal_distance > 0
        and pd.notna(risk_distance)
    ):

        increase_percent = (
            (
                risk_distance
                - normal_distance
            )
            / normal_distance
        ) * 100

    else:

        increase_percent = np.nan


    # -----------------------------------------------------
    # Isolation score
    # -----------------------------------------------------

    if pd.isna(
        increase_percent
    ):

        isolation_score = 100.0

    else:

        isolation_score = np.clip(
            increase_percent,
            0,
            100
        )


    # -----------------------------------------------------
    # Isolation level
    # -----------------------------------------------------

    if isolation_score < 25:

        isolation_level = "LOW"

    elif isolation_score < 50:

        isolation_level = "MODERATE"

    elif isolation_score < 75:

        isolation_level = "HIGH"

    else:

        isolation_level = "VERY HIGH"


    results.append({

        "village":
            village_name,

        "nearest_node":
            village_node,

        "normal_distance_m":
            normal_distance,

        "risk_adjusted_distance_m":
            risk_distance,

        "travel_cost_increase_percent":
            increase_percent,

        "isolation_score":
            isolation_score,

        "isolation_level":
            isolation_level

    })


# =========================================================
# 11. SAVE RESULTS
# =========================================================

result_df = pd.DataFrame(
    results
)


result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 12. DISPLAY RESULTS
# =========================================================

print("\n====================================")
print("VILLAGE ISOLATION ANALYSIS COMPLETE")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)


print("\nVillage isolation results:")

print(
    result_df.to_string(
        index=False
    )
)


print("\nIsolation level distribution:")

print(
    result_df[
        "isolation_level"
    ].value_counts()
)