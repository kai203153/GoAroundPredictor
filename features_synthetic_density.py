# features_synthetic_density.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sfo = pd.read_csv("data/sfo_goarounds.csv", low_memory=False)

# Clean & time parsing
sfo["time"] = pd.to_datetime(sfo["time"], utc=True, errors="coerce")
sfo["hour"] = sfo["time"].dt.hour
sfo["date"] = sfo["time"].dt.date

# Hourly landing density (approximate traffic)
hourly_counts = (
    sfo.groupby(["date", "hour"])["icao24"]
    .count()
    .reset_index(name="traffic_density_hour")
)

sfo = sfo.merge(hourly_counts, on=["date", "hour"], how="left")

# Runway-specific density
if "runway" in sfo.columns:
    runway_counts = (
        sfo.groupby(["date", "hour", "runway"])["icao24"]
        .count()
        .reset_index(name="runway_activity")
    )
    sfo = sfo.merge(runway_counts, on=["date", "hour", "runway"], how="left")

# Training-flight indicator
sfo["is_training_flight"] = (sfo["n_approaches"] > 2).astype(int)

# Synthetic Poisson traffic metric (adds small stochastic variation)
rng = np.random.default_rng(seed=42)
sfo["synthetic_density"] = rng.poisson(
    lam=(sfo["traffic_density_hour"] / sfo["traffic_density_hour"].mean()).fillna(1)
)

# Inspect results
print(sfo[["time", "runway", "has_ga", "traffic_density_hour",
           "runway_activity", "synthetic_density"]].head())

# Save feature-enriched version
sfo.to_csv("data/sfo_goarounds_features.csv", index=False)
print("💾 Saved enriched dataset -> data/sfo_goarounds_features.csv")


plt.figure(figsize=(6,4))
sfo.groupby("runway_activity")["has_ga"].mean().plot(marker="o")
plt.title("Go-around rate vs. runway traffic density")
plt.xlabel("Runway activity (flights/hour)")
plt.ylabel("Go-around rate")
plt.grid(True, alpha=0.3)
plt.show()