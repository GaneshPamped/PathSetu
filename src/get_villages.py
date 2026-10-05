import osmnx as ox
import pandas as pd

OUTPUT_FILE = "data/villages.csv"

print("Searching for villages around Gangtok...")

place = "Gangtok, Sikkim, India"

# Get places from OpenStreetMap
gdf = ox.features_from_place(
    place,
    tags={
        "place": [
            "village",
            "hamlet"
        ]
    }
)

print("\nOpenStreetMap places found:", len(gdf))

records = []

for _, row in gdf.iterrows():

    geometry = row.geometry

    if geometry is None:
        continue

    # Convert polygons/multipolygons to representative point
    point = geometry.representative_point()

    records.append({
        "village": row.get("name", "Unknown"),
        "latitude": point.y,
        "longitude": point.x
    })


villages = pd.DataFrame(records)

# Remove places without names
villages = villages[
    villages["village"].notna()
]

# Remove duplicate village names
villages = villages.drop_duplicates(
    subset=["village"]
)

# Save
villages.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n====================================")
print("VILLAGE DATA CREATED")
print("====================================")

print("\nSaved to:")
print(OUTPUT_FILE)

print("\nNumber of villages:")
print(len(villages))

print("\nFirst 20 villages:")
print(villages.head(20))