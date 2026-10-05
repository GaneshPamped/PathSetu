import folium
import osmnx as ox
import pandas as pd

print("Loading PathSetu data...")

# ==================================================
# 1. LOAD ROAD NETWORK
# ==================================================

graph = ox.load_graphml(
    "data/gangtok_roads.graphml"
)

# ==================================================
# 2. LOAD ROAD RISK DATA
# ==================================================

risk = pd.read_csv(
    "data/road_risk_explained.csv"
)

latest_date = risk["date"].max()

risk_latest = risk[
    risk["date"] == latest_date
].copy()

print(f"Latest risk date: {latest_date}")
print(f"Road risk records: {len(risk_latest)}")

# ==================================================
# 3. LOAD VILLAGE ISOLATION DATA
# ==================================================

villages = pd.read_csv(
    "data/village_isolation.csv"
)

print(f"Villages loaded: {len(villages)}")

# ==================================================
# 4. LOAD VILLAGE COORDINATES
# ==================================================

village_coordinates = pd.read_csv(
    "data/villages_connected.csv"
)

print(
    f"Village coordinate records: "
    f"{len(village_coordinates)}"
)

# ==================================================
# 5. CHECK COORDINATE COLUMNS
# ==================================================

print(
    "Coordinate file columns:"
)

print(
    list(village_coordinates.columns)
)

# ==================================================
# 6. MERGE VILLAGE DATA
# ==================================================

villages = villages.merge(
    village_coordinates[
        [
            "village",
            "latitude",
            "longitude"
        ]
    ],
    on="village",
    how="left"
)

print(
    "Village data successfully combined."
)

# ==================================================
# 7. CHECK MISSING COORDINATES
# ==================================================

missing_coordinates = villages[
    villages["latitude"].isna()
    | villages["longitude"].isna()
]

print(
    f"Villages missing coordinates: "
    f"{len(missing_coordinates)}"
)

if len(missing_coordinates) > 0:

    print(
        missing_coordinates["village"].tolist()
    )

# ==================================================
# 8. MAP CENTER
# ==================================================

map_center = [
    27.3314,
    88.6138
]

# ==================================================
# 9. CARTO API KEY
# ==================================================

CARTO_API_KEY = "cb1_4ajk_1_dc2f3717e0e930836332d5bf"

# ==================================================
# 10. CREATE MAP
# ==================================================

m = folium.Map(
    location=map_center,
    zoom_start=10,
    tiles=None
)

# ==================================================
# 11. CARTO BASEMAP
# ==================================================

carto_url = (
    "https://basemaps.cartocdn.com/"
    "rastertiles/voyager/"
    "{z}/{x}/{y}.png"
    f"?key={CARTO_API_KEY}"
)

folium.TileLayer(
    tiles=carto_url,
    name="CARTO Voyager",
    attr=(
        "© OpenStreetMap contributors, "
        "© CARTO"
    ),
    overlay=False,
    control=True,
    max_zoom=20
).add_to(m)

# ==================================================
# 12. ROAD NETWORK LAYER
# ==================================================

print("Adding road network...")

road_layer = folium.FeatureGroup(
    name="Road Network",
    show=True
)

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    if "geometry" in data:

        geometry = data["geometry"]

        coordinates = [
            [lat, lon]
            for lon, lat in geometry.coords
        ]

    else:

        node_u = graph.nodes[u]
        node_v = graph.nodes[v]

        coordinates = [
            [
                node_u["y"],
                node_u["x"]
            ],
            [
                node_v["y"],
                node_v["x"]
            ]
        ]

    folium.PolyLine(
        coordinates,
        color="gray",
        weight=1,
        opacity=0.5
    ).add_to(road_layer)

road_layer.add_to(m)

# ==================================================
# 13. VILLAGE LAYER
# ==================================================

print("Adding villages...")

village_layer = folium.FeatureGroup(
    name="Villages",
    show=True
)

for _, row in villages.iterrows():

    # Skip villages without coordinates
    if (
        pd.isna(row["latitude"])
        or pd.isna(row["longitude"])
    ):
        continue

    village_name = row["village"]

    isolation_score = float(
        row["isolation_score"]
    )

    isolation_level = row[
        "isolation_level"
    ]

    normal_distance_km = (
        float(row["normal_distance_m"])
        / 1000
    )

    risk_distance_km = (
        float(row["risk_adjusted_distance_m"])
        / 1000
    )

    travel_increase = float(
        row["travel_cost_increase_percent"]
    )

    # ----------------------------------------------
    # Popup information
    # ----------------------------------------------

    popup_text = f"""
    <div style="width:250px">

    <h4>
    PathSetu Village
    </h4>

    <b>Village:</b>
    {village_name}
    <br><br>

    <b>Isolation Score:</b>
    {isolation_score:.2f}
    <br>

    <b>Isolation Level:</b>
    {isolation_level}
    <br><br>

    <b>Normal Route:</b>
    {normal_distance_km:.2f} km
    <br>

    <b>Risk-Adjusted Route:</b>
    {risk_distance_km:.2f} km
    <br>

    <b>Travel Increase:</b>
    {travel_increase:.2f}%

    </div>
    """

    folium.CircleMarker(

        location=[
            row["latitude"],
            row["longitude"]
        ],

        radius=7,

        popup=folium.Popup(
            popup_text,
            max_width=300
        ),

        tooltip=(
            f"{village_name} | "
            f"{isolation_level}"
        ),

        fill=True,

        fill_opacity=0.9
    ).add_to(village_layer)

village_layer.add_to(m)

# ==================================================
# 14. GANGTOK REFERENCE POINT
# ==================================================

folium.Marker(

    location=map_center,

    popup=(
        "<b>Gangtok Reference Point</b>"
    ),

    tooltip="Gangtok",

    icon=folium.Icon(
        icon="home",
        prefix="fa"
    )

).add_to(m)

# ==================================================
# 15. LAYER CONTROL
# ==================================================

folium.LayerControl().add_to(m)

# ==================================================
# 16. SAVE MAP
# ==================================================

output_file = (
    "data/pathsetu_risk_map.html"
)

m.save(output_file)

# ==================================================
# 17. FINAL OUTPUT
# ==================================================

print()
print(
    "======================================"
)

print(
    "PathSetu map created successfully!"
)

print(
    "======================================"
)

print(
    f"Map saved to: {output_file}"
)

print(
    f"Latest risk date: {latest_date}"
)

print(
    f"Villages displayed: "
    f"{len(villages) - len(missing_coordinates)}"
)

print()