import osmnx as ox
import pandas as pd
import networkx as nx

print("==============================================")
print("PathSetu - Impact-Based Disaster Simulator")
print("==============================================")

# ==================================================
# 1. LOAD ROAD NETWORK
# ==================================================

graph = ox.load_graphml(
    "data/gangtok_roads.graphml"
)

print()
print(f"Road network nodes: {len(graph.nodes)}")
print(f"Road network edges: {len(graph.edges)}")

# ==================================================
# 2. LOAD VILLAGES
# ==================================================

villages = pd.read_csv(
    "data/villages_connected.csv"
)

print(
    f"Villages loaded: {len(villages)}"
)

# ==================================================
# 3. LOAD RISK DATA
# ==================================================

risk = pd.read_csv(
    "data/road_risk_explained.csv"
)

latest_date = risk["date"].max()

risk_latest = risk[
    risk["date"] == latest_date
].copy()

print(
    f"Latest risk date: {latest_date}"
)

# ==================================================
# 4. CREATE RISK LOOKUP
# ==================================================

risk_lookup = {}

for _, row in risk_latest.iterrows():

    u = int(row["road_u"])
    v = int(row["road_v"])
    key = int(row["road_key"])

    risk_lookup[
        (u, v, key)
    ] = float(row["risk_score"])

print(
    f"Risk records loaded: {len(risk_lookup)}"
)

# ==================================================
# 5. GANGTOK REFERENCE
# ==================================================

gangtok_lat = 27.3314
gangtok_lon = 88.6138

gangtok_node = ox.distance.nearest_nodes(
    graph,
    X=gangtok_lon,
    Y=gangtok_lat
)

print(
    f"Gangtok reference node: {gangtok_node}"
)

# ==================================================
# 6. CALCULATE NORMAL ROUTES
# ==================================================

print()
print("Calculating normal village routes...")

normal_distances = {}

for _, village in villages.iterrows():

    name = village["village"]

    node = int(
        village["nearest_node"]
    )

    try:

        distance = nx.shortest_path_length(
            graph,
            source=node,
            target=gangtok_node,
            weight="length"
        )

        normal_distances[name] = distance

    except nx.NetworkXNoPath:

        normal_distances[name] = None

print("Normal routes calculated.")

# ==================================================
# 7. SELECT CANDIDATE ROADS
# ==================================================

print()
print("Finding important candidate roads...")

candidates = []

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    length = float(
        data.get("length", 0)
    )

    if length <= 0:
        continue

    risk_score = risk_lookup.get(
        (int(u), int(v), int(key)),
        0
    )

    # Candidate score combines road length
    # and disaster risk.

    candidate_score = (
        0.40 * min(length / 2000, 1) * 100
        +
        0.60 * risk_score
    )

    candidates.append(
        {
            "u": u,
            "v": v,
            "key": key,
            "length_m": length,
            "risk_score": risk_score,
            "candidate_score": candidate_score
        }
    )

candidates_df = pd.DataFrame(
    candidates
)

candidates_df = candidates_df.sort_values(
    by="candidate_score",
    ascending=False
)

# Test top 100 candidates.
# This keeps the simulation practical.

candidates_df = candidates_df.head(100)

print(
    f"Candidate roads selected: "
    f"{len(candidates_df)}"
)

# ==================================================
# 8. TEST ROAD CLOSURES
# ==================================================

print()
print("Testing simulated road closures...")

closure_results = []

for index, candidate in candidates_df.iterrows():

    u = candidate["u"]
    v = candidate["v"]
    key = candidate["key"]

    test_graph = graph.copy()

    try:

        test_graph.remove_edge(
            u,
            v,
            key
        )

    except Exception:

        continue

    affected_villages = 0
    total_increase = 0
    maximum_increase = 0
    isolated_villages = 0

    for _, village in villages.iterrows():

        name = village["village"]

        node = int(
            village["nearest_node"]
        )

        normal_distance = (
            normal_distances.get(name)
        )

        if normal_distance is None:
            continue

        try:

            new_distance = (
                nx.shortest_path_length(
                    test_graph,
                    source=node,
                    target=gangtok_node,
                    weight="length"
                )
            )

        except nx.NetworkXNoPath:

            isolated_villages += 1
            affected_villages += 1

            continue

        increase_percent = (
            (
                new_distance
                - normal_distance
            )
            / normal_distance
        ) * 100

        if increase_percent > 1:

            affected_villages += 1

            total_increase += (
                increase_percent
            )

            maximum_increase = max(
                maximum_increase,
                increase_percent
            )

    average_increase = (
        total_increase / affected_villages
        if affected_villages > 0
        else 0
    )

    # Overall impact score.
    #
    # Village coverage = 50%
    # Average disruption = 30%
    # Maximum disruption = 20%

    impact_score = (
        0.50
        * (
            affected_villages
            / len(villages)
        )
        * 100
        +
        0.30
        * min(
            average_increase,
            100
        )
        +
        0.20
        * min(
            maximum_increase,
            100
        )
    )

    closure_results.append(
        {
            "u": u,
            "v": v,
            "key": key,
            "length_m": candidate["length_m"],
            "risk_score": candidate["risk_score"],
            "affected_villages": affected_villages,
            "isolated_villages": isolated_villages,
            "average_increase_percent":
                average_increase,
            "maximum_increase_percent":
                maximum_increase,
            "impact_score":
                impact_score
        }
    )

print("Road closure testing complete.")

# ==================================================
# 9. SELECT MOST IMPACTFUL ROAD
# ==================================================

results = pd.DataFrame(
    closure_results
)

if len(results) == 0:

    raise ValueError(
        "No closure simulations were completed."
    )

results = results.sort_values(
    by="impact_score",
    ascending=False
)

selected = results.iloc[0]

closure_u = selected["u"]
closure_v = selected["v"]
closure_key = selected["key"]

closure_length = selected[
    "length_m"
]

closure_risk = selected[
    "risk_score"
]

print()
print("==============================================")
print("MOST IMPACTFUL ROAD CLOSURE")
print("==============================================")

print(
    f"From node: {closure_u}"
)

print(
    f"To node: {closure_v}"
)

print(
    f"Road key: {closure_key}"
)

print(
    f"Road length: "
    f"{closure_length:.2f} meters"
)

print(
    f"Road risk: "
    f"{closure_risk:.2f}"
)

print(
    f"Impact score: "
    f"{selected['impact_score']:.2f}"
)

print(
    f"Affected villages: "
    f"{int(selected['affected_villages'])}"
)

print(
    f"Isolated villages: "
    f"{int(selected['isolated_villages'])}"
)

# ==================================================
# 10. SIMULATE FINAL CLOSURE
# ==================================================

simulated_graph = graph.copy()

simulated_graph.remove_edge(
    closure_u,
    closure_v,
    closure_key
)

# ==================================================
# 11. CALCULATE FINAL VILLAGE IMPACT
# ==================================================

final_results = []

for _, village in villages.iterrows():

    name = village["village"]

    node = int(
        village["nearest_node"]
    )

    normal_distance = (
        normal_distances.get(name)
    )

    if normal_distance is None:

        final_results.append(
            {
                "village": name,
                "normal_distance_km": None,
                "closure_distance_km": None,
                "distance_increase_percent": None,
                "impact_level":
                    "NO BASELINE ROUTE"
            }
        )

        continue

    try:

        closure_distance = (
            nx.shortest_path_length(
                simulated_graph,
                source=node,
                target=gangtok_node,
                weight="length"
            )
        )

    except nx.NetworkXNoPath:

        final_results.append(
            {
                "village": name,
                "normal_distance_km":
                    normal_distance / 1000,
                "closure_distance_km":
                    None,
                "distance_increase_percent":
                    None,
                "impact_level":
                    "ISOLATED"
            }
        )

        continue

    increase_percent = (
        (
            closure_distance
            - normal_distance
        )
        / normal_distance
    ) * 100

    if increase_percent < 5:

        impact = "LOW"

    elif increase_percent < 20:

        impact = "MODERATE"

    elif increase_percent < 50:

        impact = "HIGH"

    else:

        impact = "VERY HIGH"

    final_results.append(
        {
            "village": name,

            "normal_distance_km":
                normal_distance / 1000,

            "closure_distance_km":
                closure_distance / 1000,

            "distance_increase_percent":
                increase_percent,

            "impact_level":
                impact
        }
    )

final_df = pd.DataFrame(
    final_results
)

# ==================================================
# 12. SORT IMPACT
# ==================================================

impact_order = {
    "ISOLATED": 4,
    "VERY HIGH": 3,
    "HIGH": 2,
    "MODERATE": 1,
    "LOW": 0,
    "NO BASELINE ROUTE": -1
}

final_df["impact_rank"] = (
    final_df[
        "impact_level"
    ].map(impact_order)
)

final_df = final_df.sort_values(
    by=[
        "impact_rank",
        "distance_increase_percent"
    ],
    ascending=[
        False,
        False
    ],
    na_position="last"
)

final_df = final_df.drop(
    columns=["impact_rank"]
)

# ==================================================
# 13. ADD CLOSURE DETAILS
# ==================================================

final_df.insert(
    0,
    "closed_road_u",
    closure_u
)

final_df.insert(
    1,
    "closed_road_v",
    closure_v
)

final_df.insert(
    2,
    "closed_road_key",
    closure_key
)

final_df.insert(
    3,
    "closed_road_risk",
    closure_risk
)

# ==================================================
# 14. SAVE
# ==================================================

output_file = (
    "data/disaster_simulation.csv"
)

final_df.to_csv(
    output_file,
    index=False
)

# ==================================================
# 15. DISPLAY RESULTS
# ==================================================

print()
print("==============================================")
print("FINAL DISASTER IMPACT RESULTS")
print("==============================================")

print()

print(
    final_df.to_string(
        index=False
    )
)

# ==================================================
# 16. SUMMARY
# ==================================================

print()
print("==============================================")
print("Impact Summary")
print("==============================================")

print(
    final_df[
        "impact_level"
    ].value_counts().to_string()
)

print()
print(
    f"Output saved to: {output_file}"
)

print()
print("==============================================")
print("IMPACT-BASED DISASTER SIMULATION COMPLETE")
print("==============================================")