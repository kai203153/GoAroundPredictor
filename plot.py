import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import glob
import os
import sys

df = pd.read_csv("inbound_SFO_hour_20251108_0300.csv")

# SFO coordinates
SFO_LAT = 37.6213
SFO_LON = -122.3790

def calculate_heading_to_sfo(lat, lon):
    """Calculate heading from aircraft position to SFO in degrees"""
    # Convert to radians
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lat2, lon2 = np.radians(SFO_LAT), np.radians(SFO_LON)
    
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    
    heading = np.degrees(np.arctan2(y, x))
    # Normalize to 0-360
    heading = (heading + 360) % 360
    return heading

def classify_runway(lat, lon):
    """Classify runway based on position and heading to SFO"""
    heading = calculate_heading_to_sfo(lat, lon)
    
    # Runway 28L/28R (approaching from east, heading ~280 degrees)
    if lon > -122.5 and (260 <= heading <= 300 or heading <= 20 or heading >= 340):
        return "28L/28R"
    # Runway 19L/19R (approaching from north, heading ~190 degrees)
    elif 170 <= heading <= 210:
        return "19L/19R"
    # Runway 10L/10R (approaching from west, heading ~100 degrees)
    elif 80 <= heading <= 120:
        return "10L/10R"
    # Runway 01L/01R (approaching from south, heading ~010 degrees)
    elif 0 <= heading <= 30 or heading >= 330:
        return "01L/01R"
    else:
        return "Unknown"

df["runway_guess"] = df.apply(lambda row: classify_runway(row["lat"], row["lon"]), axis=1)

# --- 2️⃣ Plot the classified flights ---
plt.figure(figsize=(8, 8))
sns.scatterplot(data=df, x="lon", y="lat", hue="runway_guess", palette="Set1", s=60)
plt.scatter(-122.3790, 37.6213, color="black", marker="*", s=200, label="SFO")

plt.title("Inbound Flights to SFO (by Runway Guess)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.axis("equal")
plt.grid(True)
plt.show()

# Optional: check distribution by runway
print(df["runway_guess"].value_counts())