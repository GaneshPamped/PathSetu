import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

LANDSLIDE_FILE = "data/landslides.csv"
ROAD_FILE = "data/road_terrain.csv"

OUTPUT_FILE = "data/road_landslide_features.csv"

print("Loading landslide data...")

landslides = pd.read_csv(LANDSLIDE_FILE)

print("Landslide records:", len(landslides))


print("\nLoading road terrain data...")

roads = pd.read_csv(ROAD_FILE)

print("Road segments:", len(roads))


# ---------------------------------------------------------
# PART 1: Extract year from messy date information
# ---------------------------------------------------------

print("\nExtracting landslide years...")

landslides["year"] = (
    landslides["date"]
    .astype(str)
    .str.extract(r"(20\d{2})")[0]
)

landslides["year"] = pd.to_numeric(
    landslides["year"],
    errors="coerce"
)

print(
    "Records with usable year:",
    landslides["year"].notna().sum()
)

print(
    "Records without year:",
    landslides["year"].isna().sum()
)


# ---------------------------------------------------------
# PART 2: Prepare coordinates
# ---------------------------------------------------------

landslides = landslides.dropna(
    subset=["latitude", "longitude"]
).copy()

roads = roads.dropna(
    subset=["latitude", "longitude"]
).copy()


# ---------------------------------------------------------
# PART 3: Convert latitude/longitude to approximate metres
# ---------------------------------------------------------

print("\nPreparing geographic coordinates...")

# Gangtok/Sikkim is around 27 degrees latitude.
# 1 degree latitude is approximately 111 km.
#
# For longitude we multiply by cos(latitude).

mean_lat = roads["latitude"].mean()

lat_factor = 111320

lon_factor = 111320 * np.cos(
    np.radians(mean_lat)
)


def convert_coordinates(df):

    x = (
        df["longitude"].values
        * lon_factor
    )

    y = (
        df["latitude"].values
        * lat_factor
    )

    return np.column_stack((x, y))


road_coordinates = convert_coordinates(
    roads
)

landslide_coordinates = convert_coordinates(
    landslides
)


# ---------------------------------------------------------
# PART 4: Build spatial search tree
# ---------------------------------------------------------

print("\nBuilding landslide spatial index...")

tree = cKDTree(
    landslide_coordinates
)


# ---------------------------------------------------------
# PART 5: Distance to nearest landslide
# ---------------------------------------------------------

print("\nCalculating nearest landslide distance...")

distances, indexes = tree.query(
    road_coordinates,
    k=1
)

roads["distance_to_nearest_landslide_m"] = distances

roads["distance_to_nearest_landslide_km"] = (
    distances / 1000
)


# ---------------------------------------------------------
# PART 6: Count nearby landslides
# ---------------------------------------------------------

print("\nCalculating nearby landslide counts...")

# 5 km radius
RADIUS_5KM = 5000

nearby_counts = []

for coordinate in road_coordinates:

    count = len(
        tree.query_ball_point(
            coordinate,
            RADIUS_5KM
        )
    )

    nearby_counts.append(count)


roads["landslides_within_5km"] = (
    nearby_counts
)


# ---------------------------------------------------------
# PART 7: Count very nearby landslides
# ---------------------------------------------------------

print("\nCalculating landslides within 1 km...")

RADIUS_1KM = 1000

nearby_1km = []

for coordinate in road_coordinates:

    count = len(
        tree.query_ball_point(
            coordinate,
            RADIUS_1KM
        )
    )

    nearby_1km.append(count)


roads["landslides_within_1km"] = (
    nearby_1km
)


# ---------------------------------------------------------
# PART 8: Save result
# ---------------------------------------------------------

print("\nSaving landslide features...")

roads.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n====================================")
print("LANDSLIDE FEATURE PROCESSING COMPLETE")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nRoad segments processed:")
print(len(roads))

print("\nFeature statistics:")

print(
    "Average distance to nearest landslide:",
    round(
        roads[
            "distance_to_nearest_landslide_km"
        ].mean(),
        2
    ),
    "km"
)

print(
    "Minimum distance to nearest landslide:",
    round(
        roads[
            "distance_to_nearest_landslide_km"
        ].min(),
        2
    ),
    "km"
)

print(
    "Maximum distance to nearest landslide:",
    round(
        roads[
            "distance_to_nearest_landslide_km"
        ].max(),
        2
    ),
    "km"
)

print(
    "Maximum landslides within 5 km:",
    roads[
        "landslides_within_5km"
    ].max()
)

print(
    "Maximum landslides within 1 km:",
    roads[
        "landslides_within_1km"
    ].max()
)

print("\nFirst 10 records:")

print(
    roads[
        [
            "road_u",
            "road_v",
            "latitude",
            "longitude",
            "elevation_m",
            "slope_degrees",
            "distance_to_nearest_landslide_km",
            "landslides_within_1km",
            "landslides_within_5km"
        ]
    ].head(10)
)