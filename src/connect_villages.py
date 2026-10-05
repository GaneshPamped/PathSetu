import osmnx as ox
import pandas as pd
import networkx as nx

ROAD_FILE = "data/gangtok_roads.graphml"
VILLAGE_FILE = "data/villages.csv"
OUTPUT_FILE = "data/villages_connected.csv"


print("Loading road network...")

graph = ox.load_graphml(
    ROAD_FILE
)

print("Road network loaded.")

print(
    "Road network nodes:",
    len(graph.nodes)
)

print(
    "Road network edges:",
    len(graph.edges)
)


# ---------------------------------------------------------
# Load villages
# ---------------------------------------------------------

print("\nLoading village data...")

villages = pd.read_csv(
    VILLAGE_FILE
)

print(
    "Villages:",
    len(villages)
)


# ---------------------------------------------------------
# Find nearest road node
# ---------------------------------------------------------

print("\nFinding nearest road node for each village...")

nearest_nodes = ox.distance.nearest_nodes(
    graph,
    X=villages["longitude"].tolist(),
    Y=villages["latitude"].tolist()
)


villages["nearest_node"] = nearest_nodes


# ---------------------------------------------------------
# Get coordinates of nearest road nodes
# ---------------------------------------------------------

node_latitudes = []
node_longitudes = []


for node in villages["nearest_node"]:

    node_data = graph.nodes[node]

    node_longitudes.append(
        float(node_data["x"])
    )

    node_latitudes.append(
        float(node_data["y"])
    )


villages["road_node_latitude"] = node_latitudes

villages["road_node_longitude"] = node_longitudes


# ---------------------------------------------------------
# Calculate approximate village-to-road distance
# ---------------------------------------------------------

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    from math import radians, sin, cos, sqrt, atan2

    earth_radius = 6371000

    # Convert coordinates to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    lon1_rad = radians(lon1)
    lon2_rad = radians(lon2)

    # Differences
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = (
        sin(delta_lat / 2) ** 2
        +
        cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


distances = []


for _, row in villages.iterrows():

    distance = calculate_distance(
        row["latitude"],
        row["longitude"],
        row["road_node_latitude"],
        row["road_node_longitude"]
    )

    distances.append(distance)


villages["distance_to_road_m"] = distances


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

villages.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n====================================")
print("VILLAGES CONNECTED TO ROAD NETWORK")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nTotal villages:")
print(len(villages))

print("\nAverage distance to road:")
print(
    round(
        villages["distance_to_road_m"].mean(),
        2
    ),
    "metres"
)

print("\nMaximum distance to road:")
print(
    round(
        villages["distance_to_road_m"].max(),
        2
    ),
    "metres"
)

print("\nVillage connections:")

print(
    villages[
        [
            "village",
            "nearest_node",
            "distance_to_road_m"
        ]
    ].to_string(index=False)
)