import osmnx as ox
import pandas as pd
import networkx as nx
import numpy as np


# =========================================================
# FILES
# =========================================================

ROAD_FILE = "data/gangtok_roads.graphml"
VILLAGE_FILE = "data/villages_connected.csv"
RISK_FILE = "data/road_risk_dataset.csv"

OUTPUT_FILE = "data/risk_aware_routes.csv"


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

print("\nLoading villages...")

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
# 4. SELECT LATEST RISK DATE
# =========================================================

print("\nSelecting latest risk conditions...")

risk["date"] = pd.to_datetime(
    risk["date"]
)

latest_date = risk["date"].max()

print(
    "Latest risk date:",
    latest_date.date()
)


latest_risk = risk[
    risk["date"] == latest_date
].copy()

print(
    "Latest road risk records:",
    len(latest_risk)
)


# =========================================================
# 5. CREATE RISK LOOKUP
# =========================================================

print("\nCreating risk lookup...")

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


# =========================================================
# 6. ATTACH RISK TO ROAD NETWORK
# =========================================================

print("\nAttaching risk to roads...")

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


    # Safety checks

    if not np.isfinite(
        risk_value
    ):

        risk_value = 0.0


    risk_value = np.clip(
        risk_value,
        0,
        100
    )


    data["risk_score"] = float(
        risk_value
    )


print(
    "Roads matched:",
    matched
)

print(
    "Roads without risk:",
    unmatched
)


# =========================================================
# 7. CREATE ROUTE COSTS
# =========================================================

print("\nCreating route costs...")


for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    # Road length

    try:

        length = float(
            data.get(
                "length",
                1
            )
        )

    except:

        length = 1.0


    if (
        not np.isfinite(length)
        or length <= 0
    ):

        length = 1.0


    # Road risk

    risk_value = float(
        data.get(
            "risk_score",
            0
        )
    )


    # Normal route cost

    data["normal_cost"] = (
        length
    )


    # Risk-aware route cost

    data["risk_cost"] = (
        length
        * (
            1
            + risk_value / 100
        )
    )


# =========================================================
# 8. FIND GANGTOK NODE
# =========================================================

print("\nFinding Gangtok road node...")

GANGTOK_LAT = 27.3314
GANGTOK_LON = 88.6138


gangtok_node = ox.distance.nearest_nodes(
    graph,
    X=GANGTOK_LON,
    Y=GANGTOK_LAT
)


print(
    "Gangtok node:",
    gangtok_node
)


# =========================================================
# 9. CALCULATE ROUTES
# =========================================================

results = []


print("\nCalculating routes...")


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
        "\nProcessing:",
        village_name
    )


    # -----------------------------------------------------
    # NORMAL SHORTEST ROUTE
    # -----------------------------------------------------

    try:

        normal_route = (
            nx.shortest_path(
                graph,
                village_node,
                gangtok_node,
                weight="normal_cost"
            )
        )

        normal_distance = (
            nx.path_weight(
                graph,
                normal_route,
                weight="normal_cost"
            )
        )

    except nx.NetworkXNoPath:

        normal_route = []

        normal_distance = np.nan


    # -----------------------------------------------------
    # RISK-AWARE ROUTE
    # -----------------------------------------------------

    try:

        safe_route = (
            nx.shortest_path(
                graph,
                village_node,
                gangtok_node,
                weight="risk_cost"
            )
        )

        safe_cost = (
            nx.path_weight(
                graph,
                safe_route,
                weight="risk_cost"
            )
        )

    except nx.NetworkXNoPath:

        safe_route = []

        safe_cost = np.nan


    # -----------------------------------------------------
    # Calculate actual distance of safe route
    # -----------------------------------------------------

    if len(safe_route) > 1:

        safe_distance = 0.0

        for i in range(
            len(safe_route) - 1
        ):

            u = safe_route[i]

            v = safe_route[i + 1]

            edge_data = graph.get_edge_data(
                u,
                v
            )

            if edge_data:

                # Choose shortest edge
                # if multiple edges exist

                edge = min(
                    edge_data.values(),
                    key=lambda x: float(
                        x.get(
                            "length",
                            1
                        )
                    )
                )

                safe_distance += float(
                    edge.get(
                        "length",
                        1
                    )
                )

    else:

        safe_distance = np.nan


    # -----------------------------------------------------
    # Calculate extra distance
    # -----------------------------------------------------

    if (
        pd.notna(normal_distance)
        and pd.notna(safe_distance)
        and normal_distance > 0
    ):

        extra_distance = (
            safe_distance
            - normal_distance
        )

        extra_percentage = (
            extra_distance
            / normal_distance
        ) * 100

    else:

        extra_distance = np.nan

        extra_percentage = np.nan


    # -----------------------------------------------------
    # Calculate average risk of safe route
    # -----------------------------------------------------

    safe_route_risks = []


    for i in range(
        len(safe_route) - 1
    ):

        u = safe_route[i]

        v = safe_route[i + 1]

        edge_data = graph.get_edge_data(
            u,
            v
        )

        if edge_data:

            edge = min(
                edge_data.values(),
                key=lambda x: float(
                    x.get(
                        "length",
                        1
                    )
                )
            )

            safe_route_risks.append(
                float(
                    edge.get(
                        "risk_score",
                        0
                    )
                )
            )


    if safe_route_risks:

        average_safe_risk = np.mean(
            safe_route_risks
        )

        maximum_safe_risk = np.max(
            safe_route_risks
        )

    else:

        average_safe_risk = np.nan

        maximum_safe_risk = np.nan


    # -----------------------------------------------------
    # Calculate average risk of normal route
    # -----------------------------------------------------

    normal_route_risks = []


    for i in range(
        len(normal_route) - 1
    ):

        u = normal_route[i]

        v = normal_route[i + 1]

        edge_data = graph.get_edge_data(
            u,
            v
        )

        if edge_data:

            edge = min(
                edge_data.values(),
                key=lambda x: float(
                    x.get(
                        "length",
                        1
                    )
                )
            )

            normal_route_risks.append(
                float(
                    edge.get(
                        "risk_score",
                        0
                    )
                )
            )


    if normal_route_risks:

        average_normal_risk = np.mean(
            normal_route_risks
        )

        maximum_normal_risk = np.max(
            normal_route_risks
        )

    else:

        average_normal_risk = np.nan

        maximum_normal_risk = np.nan


    # -----------------------------------------------------
    # Save result
    # -----------------------------------------------------

    results.append({

        "village":
            village_name,

        "normal_distance_km":
            normal_distance / 1000
            if pd.notna(normal_distance)
            else np.nan,

        "safe_distance_km":
            safe_distance / 1000
            if pd.notna(safe_distance)
            else np.nan,

        "extra_distance_km":
            extra_distance / 1000
            if pd.notna(extra_distance)
            else np.nan,

        "extra_distance_percent":
            extra_percentage,

        "normal_average_risk":
            average_normal_risk,

        "safe_average_risk":
            average_safe_risk,

        "normal_max_risk":
            maximum_normal_risk,

        "safe_max_risk":
            maximum_safe_risk,

        "normal_route_nodes":
            len(normal_route),

        "safe_route_nodes":
            len(safe_route)

    })


# =========================================================
# 10. SAVE RESULTS
# =========================================================

result_df = pd.DataFrame(
    results
)


result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 11. DISPLAY RESULTS
# =========================================================

print("\n====================================")
print("RISK-AWARE ROUTING COMPLETE")
print("====================================")


print("\nSaved to:")

print(
    OUTPUT_FILE
)


print("\nRouting results:")

print(
    result_df.to_string(
        index=False
    )
)