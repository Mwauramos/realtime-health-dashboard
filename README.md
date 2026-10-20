# Real-Time Health Metrics Dashboard

A live-streaming patient vitals monitoring dashboard simulating real-time health data from Kenya county hospitals, with automatic critical alert detection and county-level analytics.

## Features

- Simulated real-time patient vitals stream (heart rate, SpO2, blood pressure, temperature) generated every second
- Auto-refreshing dashboard updating every 2 seconds
- Critical alert detection with clinical thresholds (tachycardia, bradycardia, hypotension, low SpO2, fever, hypothermia)
- County-level readings and critical event breakdown across 10 Kenya counties
- Live KPI tiles: total readings, critical alerts, average vitals, active hospitals

## Tech Stack

- Python 3.10
- Plotly Dash
- Plotly
- pandas
- NumPy
- Threading (Kafka simulation)

## Setup

```bash
conda create -n realtime-dashboard python=3.10 --copy -y
conda activate realtime-dashboard
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open your browser at `http://127.0.0.1:8050`

## Project Structure

    realtime-health-dashboard/
    ├── app.py
    ├── requirements.txt
    └── src/
        ├── producer.py
        ├── consumer.py
        └── data_store.py

## Author

ZENIK.AI | Amos Mwaura  
mwauramos.n@gmail.com
