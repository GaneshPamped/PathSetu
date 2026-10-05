import osmnx as ox
import rasterio
import pandas as pd
import numpy as np
from pyproj import Transformer

ROAD_FILE = "data/gangtok_roads.graphml"
DEM_FILE = "data/elevation/gangtok_dem_utm.tif"
SLOPE_FILE = "data/elevation/gangtok_slope_corrected.tif"

OUTPUT_FILE = "data/road_terrain.csv"

print("Loading road network...")

graph = ox.load_graphml(ROAD_FILE)

print("Road network loaded.")
print("Number of road segments:", len(graph.edges))

print("\nLoading elevation data...")

dem = rasterio.open(DEM_FILE)

print("Loading corrected slope data...")

slope = rasterio.open(SLOPE_FILE)

# Convert longitude/latitude coordinates
# into the coordinate system used by the slope raster.
transformer = Transformer.from_crs(
    "EPSG:4326",
    slope.crs,
    always_xy=True
)


def get_raster_value(dataset, x, y):

    try:

        row, col = dataset.index(x, y)

        if (
            row < 0
            or col < 0
            or row >= dataset.height
            or col >= dataset.width
        ):
            return np.nan

        value = dataset.read(1)[row, col]

        if np.isfinite(value):
            return float(value)

        return np.nan

    except Exception:

        return np.nan


records = []

print("\nExtracting terrain information...")

for u, v, key, data in graph.edges(
    keys=True,
    data=True
):

    # Find midpoint of road segment

    if "geometry" in data:

        geometry = data["geometry"]

        midpoint = geometry.interpolate(
            0.5,
            normalized=True
        )

        longitude = midpoint.x
        latitude = midpoint.y

    else:

        longitude = float(
            graph.nodes[u]["x"]
        )

        latitude = float(
            graph.nodes[u]["y"]
        )

    # Convert road coordinate
    # from longitude/latitude to UTM metres

    x, y = transformer.transform(
        longitude,
        latitude
    )

    elevation = get_raster_value(
        dem,
        x,
        y
    )

    slope_value = get_raster_value(
        slope,
        x,
        y
    )

    records.append({

        "road_u": u,

        "road_v": v,

        "road_key": key,

        "latitude": latitude,

        "longitude": longitude,

        "elevation_m": elevation,

        "slope_degrees": slope_value
    })


terrain_df = pd.DataFrame(records)

# Remove obviously impossible slope values
terrain_df.loc[
    terrain_df["slope_degrees"] > 90,
    "slope_degrees"
] = np.nan

terrain_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nTerrain data successfully created!")

print("Saved to:", OUTPUT_FILE)

print(
    "\nTotal road segments:",
    len(terrain_df)
)

print(
    "Missing elevation values:",
    terrain_df["elevation_m"].isna().sum()
)

print(
    "Missing slope values:",
    terrain_df["slope_degrees"].isna().sum()
)

print("\nTerrain statistics:")

print(
    "Average elevation:",
    round(
        terrain_df["elevation_m"].mean(),
        2
    ),
    "m"
)

print(
    "Minimum slope:",
    round(
        terrain_df["slope_degrees"].min(),
        2
    ),
    "degrees"
)

print(
    "Maximum slope:",
    round(
        terrain_df["slope_degrees"].max(),
        2
    ),
    "degrees"
)

print(
    "Average slope:",
    round(
        terrain_df["slope_degrees"].mean(),
        2
    ),
    "degrees"
)

print("\nFirst 10 records:")

print(
    terrain_df.head(10)
)