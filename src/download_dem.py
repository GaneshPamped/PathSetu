import requests
import os

# Expanded area around Gangtok
SOUTH = 27.15
NORTH = 27.50
WEST = 88.35
EAST = 88.85

API_KEY = "a0f27de85aef5ffeb6c5acaf8cb6843b"

url = "https://portal.opentopography.org/API/globaldem"

params = {
    "demtype": "COP30",
    "south": SOUTH,
    "north": NORTH,
    "west": WEST,
    "east": EAST,
    "outputFormat": "GTiff",
    "API_Key": API_KEY
}

output_file = "data/elevation/gangtok_dem.tif"

print("Downloading expanded Copernicus 30m DEM...")
print("Area:")
print("South:", SOUTH)
print("North:", NORTH)
print("West:", WEST)
print("East:", EAST)

response = requests.get(url, params=params)

print("\nServer response:", response.status_code)

if response.status_code == 200:

    with open(output_file, "wb") as file:
        file.write(response.content)

    print("\nDEM downloaded successfully!")

    print("Saved to:")
    print(output_file)

    print(
        "File size:",
        os.path.getsize(output_file),
        "bytes"
    )

else:

    print("\nDEM download failed.")

    print("Status code:", response.status_code)

    print("\nServer message:")

    print(response.text[:1000])