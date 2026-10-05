import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

input_file = "data/elevation/gangtok_dem.tif"

elevation_output = "data/elevation/gangtok_dem_utm.tif"
slope_output = "data/elevation/gangtok_slope_corrected.tif"

print("Opening original DEM...")

with rasterio.open(input_file) as src:

    # Gangtok is in UTM Zone 45N
    dst_crs = "EPSG:32645"

    transform, width, height = calculate_default_transform(
        src.crs,
        dst_crs,
        src.width,
        src.height,
        *src.bounds
    )

    dem_utm = np.empty(
        (height, width),
        dtype=np.float32
    )

    print("Reprojecting DEM to UTM...")

    reproject(
        source=rasterio.band(src, 1),
        destination=dem_utm,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        resampling=Resampling.bilinear
    )

    print("DEM reprojected successfully.")

    xres = transform.a
    yres = abs(transform.e)

    print("Pixel size:")
    print("X:", xres, "metres")
    print("Y:", yres, "metres")

    # Save reprojected elevation
    profile = src.profile.copy()

    profile.update(
        crs=dst_crs,
        transform=transform,
        width=width,
        height=height,
        dtype=rasterio.float32,
        count=1,
        compress="lzw"
    )

    print("Saving reprojected elevation...")

    with rasterio.open(
        elevation_output,
        "w",
        **profile
    ) as dst:

        dst.write(
            dem_utm.astype(np.float32),
            1
        )

    # Calculate slope
    print("Calculating slope...")

    dzdx = np.gradient(
        dem_utm,
        axis=1
    ) / xres

    dzdy = np.gradient(
        dem_utm,
        axis=0
    ) / yres

    slope = np.degrees(
        np.arctan(
            np.sqrt(
                dzdx ** 2 +
                dzdy ** 2
            )
        )
    )

    print("Saving corrected slope...")

    with rasterio.open(
        slope_output,
        "w",
        **profile
    ) as dst:

        dst.write(
            slope.astype(np.float32),
            1
        )

print("\nTerrain processing complete!")

print("Elevation saved to:")
print(elevation_output)

print("\nSlope saved to:")
print(slope_output)

print("\nSlope statistics:")

print(
    "Minimum:",
    round(float(np.nanmin(slope)), 2),
    "degrees"
)

print(
    "Maximum:",
    round(float(np.nanmax(slope)), 2),
    "degrees"
)

print(
    "Average:",
    round(float(np.nanmean(slope)), 2),
    "degrees"
)