import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from haversine import haversine

# Load flight data
df = pd.read_csv("sfo_landing_paths.csv")

# --- Step 1: Define merge checkpoints ---
MERGE_POINTS = {
    "28L": (37.545, -122.215),   # slightly south, left runway
    "28R": (37.561, -122.191)    # slightly north, right runway
}
TOUCHDOWN_POINTS = {
    "28L": (37.612, -122.359),  
    "28R": (37.57, -122.22)
}
RADIUS = {"28L": 0.0005, "28R": 0.0005}


def in_circle(lat, lon, center, r=RADIUS):
    return np.sqrt((lat - center[0])**2 + (lon - center[1])**2) < r

def classify_flight(sub):
    # --- distance to merge zones ---
    dist_l_merge = np.sqrt((sub.lat - MERGE_POINTS["28L"][0])**2 + (sub.lon - MERGE_POINTS["28L"][1])**2)
    dist_r_merge = np.sqrt((sub.lat - MERGE_POINTS["28R"][0])**2 + (sub.lon - MERGE_POINTS["28R"][1])**2)

    # --- distance to touchdown points ---
    dist_l_touch = np.sqrt((sub.lat - TOUCHDOWN_POINTS["28L"][0])**2 + (sub.lon - TOUCHDOWN_POINTS["28L"][1])**2)
    dist_r_touch = np.sqrt((sub.lat - TOUCHDOWN_POINTS["28R"][0])**2 + (sub.lon - TOUCHDOWN_POINTS["28R"][1])**2)

    # Minimum distances (for reference)
    min_l_merge = dist_l_merge.min()
    min_r_merge = dist_r_merge.min()
    min_l_touch = dist_l_touch.min()
    min_r_touch = dist_r_touch.min()

    # --- classification logic ---
    within_r = min_r_touch < RADIUS["28R"]  # 28R still uses merge classification

    # 28L: classify based on landing (touchdown) position
    within_l = min_l_touch < RADIUS["28L"]  # ~0.7 NM, strict touchdown proximity

    if within_l and not within_r:
        return "28L"
    if within_r and not within_l:
        return "28R"
    if within_l and within_r:
        # rare: choose whichever it approached closer to at touchdown
        return "28L" if min_l_touch <= min_r_touch else "28R"

    return None

# --- Step 2: Classify each aircraft ---
clean_groups = []
counts = {"28L": 0, "28R": 0, "excluded": 0}

for callsign, sub in df.groupby("callsign"):
    runway = classify_flight(sub)
    if runway:
        counts[runway] += 1
        sub = sub.assign(runway=runway)
        clean_groups.append(sub)
    else:
        counts["excluded"] += 1

df_clean = pd.concat(clean_groups, ignore_index=True)
print(f"✅ Filtered dataset: {len(df_clean)} points, {df_clean.callsign.nunique()} flights total.")
print(f"   28L: {counts['28L']} flights, 28R: {counts['28R']} flights, excluded: {counts['excluded']}")

# --- Step 3: Build smoothed reference path per runway ---
SFO = (37.6188, -122.375)

def crop_to_approach(sub, merge_lat, merge_lon, runway):
    sub = sub.sort_values("timestamp").reset_index(drop=True)
    sub["dist_to_rwy"] = [haversine((lat, lon), SFO) for lat, lon in zip(sub["lat"], sub["lon"])]

    # --- determine starting point (merge zone or later) ---
    merge_dist = [haversine((lat, lon), (merge_lat, merge_lon)) for lat, lon in zip(sub["lat"], sub["lon"])]
    merge_idx = np.argmin(merge_dist)
    cropped = sub.loc[merge_idx:].copy()

    # --- 28L special case ---
    if runway == "28L":
        # remove early overflight: before turning inbound (when longitude increasing eastward)
        lon_diff = cropped["lon"].diff().fillna(0)
        inbound = lon_diff < 0  # moving west
        if inbound.any():
            inbound_start = inbound.idxmax()
            cropped = cropped.loc[inbound_start:]

        # remove false loops south of the final path
        cropped = cropped[cropped["lat"] > 37.53]

    # --- stop after passing the runway ---
    cropped = cropped[cropped["dist_to_rwy"] > 1]  # >1 km before runway
    cropped = cropped[cropped["dist_to_rwy"] < 20]  # within ~20 km of runway

    return cropped


def build_dense_reference(df, runway, bins=250):
    """Build smooth path only from approach segments."""
    merge_lat, merge_lon = MERGE_POINTS[runway]
    grouped = []
    for callsign, sub in df[df.runway == runway].groupby("callsign"):
        cropped = crop_to_approach(sub, merge_lat, merge_lon, runway)
        if len(cropped) > 5:
            grouped.append(cropped)

    if not grouped:
        return pd.DataFrame()

    df_approach = pd.concat(grouped, ignore_index=True)

    # Bin longitudinally, but keep many bins for density
    df_approach["lon_bin"] = pd.cut(df_approach["lon"], bins=bins)
    path = (
        df_approach.groupby("lon_bin", observed=True)[["lat", "lon"]]
        .median()  # median resists outliers
        .dropna()
        .reset_index(drop=True)
    )
    return path

runways = {}
for rw in ["28L", "28R"]:
    path = build_dense_reference(df_clean, rw)
    if not path.empty:
        runways[rw] = path
        path.to_csv(f"ref_path_{rw}.csv", index=False)
        print(f"✅ Built reference path for {rw}: {len(path)} points (final approach only).")
    else:
        print(f"⚠️ No valid approach path for {rw}.")

print("\nRunway summary:")
for k, v in runways.items():
    print(f"  {k}: {len(v)} reference points (approach phase)")


df_all = pd.read_csv("sfo_landing_paths.csv")
path_28L = pd.read_csv("ref_path_28L.csv")
path_28R = pd.read_csv("ref_path_28R.csv")

# Create plot
plt.figure(figsize=(9, 9))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-123.2, -121.5, 36.8, 38.3])
ax.coastlines()
ax.gridlines(draw_labels=True)

# Plot raw points (black)
plt.scatter(df_all["lon"], df_all["lat"], s=1, color="black", alpha=0.3, transform=ccrs.PlateCarree(), label="All Flights")

# Plot runway reference paths
plt.plot(path_28L["lon"], path_28L["lat"], color="red", linewidth=2.5, label="Runway 28L Path", transform=ccrs.PlateCarree())
plt.plot(path_28R["lon"], path_28R["lat"], color="blue", linewidth=2.5, label="Runway 28R Path", transform=ccrs.PlateCarree())

plt.title("SFO Inbound Flight Paths with Runway 28L and 28R References", fontsize=12)
plt.legend(loc="lower left")
plt.show()
