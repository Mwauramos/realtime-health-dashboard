import time
import random
import threading
import numpy as np
from datetime import datetime
from src.data_store import add_vital, KENYA_COUNTIES, HOSPITALS

patient_counter = 0
counter_lock = threading.Lock()


def generate_vital() -> dict:
    global patient_counter
    with counter_lock:
        patient_counter += 1
        pid = patient_counter

    idx = random.randint(0, len(KENYA_COUNTIES) - 1)
    county = KENYA_COUNTIES[idx]
    hospital = HOSPITALS[idx]

    heart_rate = int(np.random.normal(80, 15))
    systolic = int(np.random.normal(120, 20))
    diastolic = int(np.random.normal(80, 12))
    spo2 = round(np.random.normal(97, 2), 1)
    temperature = round(np.random.normal(37.0, 0.8), 1)

    heart_rate = max(30, min(200, heart_rate))
    systolic = max(70, min(220, systolic))
    diastolic = max(40, min(140, diastolic))
    spo2 = max(70.0, min(100.0, spo2))
    temperature = max(34.0, min(42.0, temperature))

    is_critical = (
        heart_rate > 130 or heart_rate < 45 or
        systolic > 180 or systolic < 80 or
        spo2 < 92 or
        temperature > 39.5 or temperature < 35.5
    )

    alert_message = ""
    if is_critical:
        flags = []
        if heart_rate > 130: flags.append(f"Tachycardia HR={heart_rate}")
        if heart_rate < 45: flags.append(f"Bradycardia HR={heart_rate}")
        if systolic > 180: flags.append(f"Hypertensive Crisis BP={systolic}/{diastolic}")
        if systolic < 80: flags.append(f"Hypotension BP={systolic}/{diastolic}")
        if spo2 < 92: flags.append(f"Low SpO2={spo2}%")
        if temperature > 39.5: flags.append(f"High Fever Temp={temperature}C")
        if temperature < 35.5: flags.append(f"Hypothermia Temp={temperature}C")
        alert_message = " | ".join(flags)

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "patient_id": f"KE-{pid:04d}",
        "county": county,
        "hospital": hospital,
        "heart_rate": heart_rate,
        "systolic": systolic,
        "diastolic": diastolic,
        "spo2": spo2,
        "temperature": temperature,
        "is_critical": is_critical,
        "alert_message": alert_message
    }


def start_producer(interval: float = 1.0):
    def run():
        while True:
            record = generate_vital()
            add_vital(record)
            time.sleep(interval)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("Producer started: generating vitals every 1 second")