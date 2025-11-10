# ✈️ Go-Around Predictor (SFO)

**Go-Around Predictor** is a data project exploring **why aircraft abort landings** at San Francisco International Airport (SFO).  
It combines **real-time flight data** from the OpenSky Network API with **historical go-around records** to visualize air traffic and analyze contributing factors.

---

## 🎯 Motivation

As an aviation and data enthusiast, I wanted to understand what leads pilots to abort landings — a rare but critical safety maneuver.  
This project was built to **combine live aircraft data with real-world operational events**, bridging aviation systems, data science, and engineering.

---

## 🧠 Features

- 🌐 **Real-time flight tracking** using OpenSky API (OAuth2)  
- 📊 **Data visualization** of aircraft positions on map tiles  
- 🧩 **Historical data integration** using a public go-around dataset from Zenodo  
- ✈️ **Focus on SFO arrivals** (Runways 28L/28R)  
- ⚙️ Modular structure: separate files for data fetching, bbox utilities, and analysis

---

## 📁 Project Structure

    goaroundPredictor/
    ├── fetch_live_data.py      # Retrieves live aircraft data from OpenSky API
    ├── bbox_utils.py           # Bounding-box presets optimized for SFO approaches
    ├── main.py                 # Orchestrates fetching, filtering, and visualization
    ├── data/                   # Data storage (not included in repo)
    ├── .gitignore
    └── README.md

---

## 🗺️ Example Output

- Live aircraft positions plotted over the Bay Area  
- Real basemap overlay (CartoDB Positron)  
- Summary of go-around frequency for KSFO  

*(You can add screenshots here — for example, one showing live flight dots near SFO.)*

---

## 🔮 Next Steps

- Add proximity-based traffic density metrics  
- Classify weather vs. traffic-related go-arounds  
- Develop a predictive model for real-time go-around likelihood  

---

## 🧰 Tech Stack

**Python**, **Pandas**, **GeoPandas**, **Matplotlib**, **Contextily**, **Requests**  
API: **OpenSky Network**

---

## 📚 Dataset Reference

- **Go-Arounds 2022 Dataset** — Zenodo (2022)  
  [https://zenodo.org/records/7148117](https://zenodo.org/records/7148117)

---

## 💡 What I Learned

- Integrating **real-time APIs** (OAuth2 authentication) into a data pipeline  
- Managing large geospatial datasets efficiently  
- Building modular Python scripts for fetching, cleaning, and visualization  
- Using **data visualization** to interpret aviation and operational data  

---

## 🧑‍💻 Author

**Kai Sato**  
Industrial Engineering & Operations Research @ UC Berkeley  
*Passionate about finance, data, and the systems that connect the world.*
