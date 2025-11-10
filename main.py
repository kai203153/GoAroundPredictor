import pandas as pd
from fetch_live_data import fetch_flights
from bbox_utils import get_bbox
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt

bbox = get_bbox("balanced")   # or "tight", "max1credit"
df_live = fetch_flights(bbox=bbox)
print(f"✅ Fetched {len(df_live)} live flights in region {bbox}")
print(df_live.head())

goaround_df = pd.read_csv("data/go_arounds_augmented.csv")
sfo_df = goaround_df[goaround_df["airport"] == "KSFO"]
print(f"✅ Loaded {len(sfo_df)} KSFO landing records ({sfo_df['has_ga'].sum()} go-arounds)")


sfo_df.to_csv("data/sfo_goarounds.csv", index=False)


plt.figure(figsize=(6,6))
plt.scatter(df_live["longitude"], df_live["latitude"], alpha=0.5)
plt.title("Live Aircraft Positions near KSFO")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.axis("equal")  
plt.show()

if not df_live.empty:
    gdf = gpd.GeoDataFrame(
        df_live,
        geometry=gpd.points_from_xy(df_live["longitude"], df_live["latitude"]),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)

    ax = gdf.plot(figsize=(8,8), alpha=0.5, markersize=5, color="blue")
    ctx.add_basemap(ax, source=ctx.providers.Stamen.Terrain)
    plt.title("Live Flights near SFO")
    plt.show()
else:
    print("⚠️ No live flights fetched — skipping basemap plot.")
