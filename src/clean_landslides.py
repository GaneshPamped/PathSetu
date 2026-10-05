import geopandas as gpd
import pandas as pd
import os

INPUT_FILE = "data/Google_Earth_landslides_point_21Dec2021.shp"
OUTPUT_FILE = "data/landslides.csv"

print("Loading landslide shapefile...")

gdf = gpd.read_file(INPUT_FILE)

print("Shapefile loaded successfully!")

print("\nNumber of landslide records:")
print(len(gdf))

print("\nOriginal columns:")
print(list(gdf.columns))

print("\nCoordinate system:")
print(gdf.crs)

print("\nExtracting coordinates...")

# Convert to latitude/longitude
gdf = gdf.to_crs("EPSG:4326")

# Create output dataframe
landslides = pd.DataFrame()

# Event ID
landslides["event_id"] = range(1, len(gdf) + 1)

# Extract year/date information
landslides["date"] = gdf["descriptio"]

# Landslide type
landslides["location"] = gdf["Extent"]

# Landslide type/severity information
landslides["severity"] = gdf["Name"]

# Geographic coordinates
landslides["latitude"] = gdf.geometry.y
landslides["longitude"] = gdf.geometry.x

# Source
landslides["source"] = (
    "Southern Sikkim Google Earth Landslide Inventory"
)

# Remove records without coordinates
landslides = landslides.dropna(
    subset=["latitude", "longitude"]
)

# Save
landslides.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nLandslide dataset created successfully!")

print("Saved to:")
print(OUTPUT_FILE)

print("\nTotal valid landslide records:")
print(len(landslides))

print("\nLatitude range:")
print(
    landslides["latitude"].min(),
    "to",
    landslides["latitude"].max()
)

print("\nLongitude range:")
print(
    landslides["longitude"].min(),
    "to",
    landslides["longitude"].max()
)

print("\nFirst 10 records:")
print(landslides.head(10))