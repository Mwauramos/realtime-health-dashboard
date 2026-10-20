from src.data_store import get_vitals_df, get_alerts_df, get_summary_stats


def get_latest_vitals(n: int = 50):
    df = get_vitals_df()
    if df.empty:
        return df
    return df.tail(n).reset_index(drop=True)


def get_county_summary():
    df = get_vitals_df()
    if df.empty:
        return {}
    summary = df.groupby("county").agg(
        readings=("patient_id", "count"),
        critical=("is_critical", "sum"),
        avg_hr=("heart_rate", "mean"),
        avg_spo2=("spo2", "mean")
    ).round(1).reset_index()
    return summary


def get_recent_alerts(n: int = 10):
    df = get_alerts_df()
    if df.empty:
        return df
    return df.tail(n).reset_index(drop=True)


def get_stats():
    df = get_vitals_df()
    return get_summary_stats(df)