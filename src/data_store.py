import pandas as pd
import numpy as np
from datetime import datetime
from collections import deque
import threading

MAX_RECORDS = 200

store_lock = threading.Lock()

vitals_store = deque(maxlen=MAX_RECORDS)
alerts_store = deque(maxlen=50)

KENYA_COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Thika", "Malindi", "Kitale", "Garissa", "Kakamega"
]

HOSPITALS = [
    "Kenyatta National Hospital", "Coast General Hospital",
    "Jaramogi Oginga Odinga Hospital", "Nakuru Level 5",
    "Moi Teaching and Referral Hospital", "Thika Level 5",
    "Malindi District Hospital", "Kitale County Hospital",
    "Garissa County Referral", "Kakamega County General"
]


def add_vital(record: dict):
    with store_lock:
        vitals_store.append(record)
        if record.get("is_critical"):
            alerts_store.append({
                "time": record["timestamp"],
                "patient_id": record["patient_id"],
                "hospital": record["hospital"],
                "county": record["county"],
                "alert": record["alert_message"]
            })


def get_vitals_df() -> pd.DataFrame:
    with store_lock:
        if not vitals_store:
            return pd.DataFrame()
        return pd.DataFrame(list(vitals_store))


def get_alerts_df() -> pd.DataFrame:
    with store_lock:
        if not alerts_store:
            return pd.DataFrame()
        return pd.DataFrame(list(alerts_store))


def get_summary_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    return {
        "total_readings": len(df),
        "critical_count": int(df["is_critical"].sum()),
        "avg_heart_rate": round(df["heart_rate"].mean(), 1),
        "avg_spo2": round(df["spo2"].mean(), 1),
        "avg_temperature": round(df["temperature"].mean(), 1),
        "active_hospitals": df["hospital"].nunique()
    }