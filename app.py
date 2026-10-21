import sys
import os
import threading

sys.path.insert(0, os.path.dirname(__file__))

from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd

from src.producer import start_producer
from src.consumer import get_latest_vitals, get_county_summary, get_recent_alerts, get_stats

app = Dash(__name__)
app.title = "ZENIK.AI | Real-Time Health Metrics"
server = app.server  # expose Flask server for gunicorn

# Ensure producer starts exactly once across all gunicorn workers
_producer_started = False
_producer_lock = threading.Lock()

def ensure_producer():
    global _producer_started
    with _producer_lock:
        if not _producer_started:
            start_producer(interval=1.0)
            _producer_started = True

ensure_producer()

app.layout = html.Div(style={"backgroundColor": "#0f1117", "minHeight": "100vh", "fontFamily": "Arial, sans-serif", "padding": "20px"}, children=[

    html.H1("🏥 Real-Time Health Metrics Dashboard",
            style={"color": "#ffffff", "textAlign": "center", "marginBottom": "5px"}),
    html.Hr(style={"borderColor": "#333"}),

    dcc.Interval(id="interval", interval=2000, n_intervals=0),

    # KPI row
    html.Div(id="kpi-row", style={"display": "flex", "gap": "20px", "marginBottom": "20px"}),

    # Charts row 1
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "20px"}, children=[
        html.Div(dcc.Graph(id="hr-chart"), style={"flex": "1"}),
        html.Div(dcc.Graph(id="spo2-chart"), style={"flex": "1"}),
    ]),

    # Charts row 2
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "20px"}, children=[
        html.Div(dcc.Graph(id="bp-chart"), style={"flex": "1"}),
        html.Div(dcc.Graph(id="temp-chart"), style={"flex": "1"}),
    ]),

    # County summary and alerts
    html.Div(style={"display": "flex", "gap": "20px"}, children=[
        html.Div(dcc.Graph(id="county-chart"), style={"flex": "1"}),
        html.Div([
            html.H3("Critical Alerts", style={"color": "#ff4444", "marginBottom": "10px"}),
            html.Div(id="alerts-table")
        ], style={"flex": "1", "backgroundColor": "#1a1a2e", "padding": "15px", "borderRadius": "8px"}),
    ]),
])


def kpi_card(label, value, color="#00d4ff"):
    return html.Div(style={
        "backgroundColor": "#1a1a2e", "padding": "15px 25px",
        "borderRadius": "8px", "flex": "1", "textAlign": "center",
        "borderTop": f"3px solid {color}"
    }, children=[
        html.Div(label, style={"color": "#aaaaaa", "fontSize": "13px", "marginBottom": "5px"}),
        html.Div(str(value), style={"color": color, "fontSize": "28px", "fontWeight": "bold"})
    ])


chart_layout = dict(
    plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e",
    font=dict(color="#cccccc"), margin=dict(l=40, r=20, t=40, b=30),
    xaxis=dict(gridcolor="#2a2a3e"), yaxis=dict(gridcolor="#2a2a3e")
)


@app.callback(
    Output("kpi-row", "children"),
    Output("hr-chart", "figure"),
    Output("spo2-chart", "figure"),
    Output("bp-chart", "figure"),
    Output("temp-chart", "figure"),
    Output("county-chart", "figure"),
    Output("alerts-table", "children"),
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    # Ensure producer is running (in case worker restarted)
    ensure_producer()

    df = get_latest_vitals(100)
    stats = get_stats()
    county_df = get_county_summary()
    alerts_df = get_recent_alerts(8)

    if df.empty:
        empty_fig = go.Figure(layout=chart_layout)
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, []

    kpis = [
        kpi_card("Total Readings", stats.get("total_readings", 0)),
        kpi_card("Critical Alerts", stats.get("critical_count", 0), "#ff4444"),
        kpi_card("Avg Heart Rate", f"{stats.get('avg_heart_rate', 0)} bpm", "#00ff88"),
        kpi_card("Avg SpO2", f"{stats.get('avg_spo2', 0)}%", "#ffaa00"),
        kpi_card("Avg Temp", f"{stats.get('avg_temperature', 0)}°C", "#aa88ff"),
        kpi_card("Active Hospitals", stats.get("active_hospitals", 0), "#00d4ff"),
    ]

    hr_fig = go.Figure(layout=chart_layout)
    hr_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["heart_rate"],
                                mode="lines", line=dict(color="#00ff88", width=1.5),
                                fill="tozeroy", fillcolor="rgba(0,255,136,0.1)"))
    hr_fig.update_layout(title="Heart Rate (bpm)")
    hr_fig.add_hline(y=130, line_dash="dash", line_color="#ff4444", annotation_text="Critical")

    spo2_fig = go.Figure(layout=chart_layout)
    spo2_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["spo2"],
                                  mode="lines", line=dict(color="#ffaa00", width=1.5),
                                  fill="tozeroy", fillcolor="rgba(255,170,0,0.1)"))
    spo2_fig.update_layout(title="SpO2 (%)")
    spo2_fig.add_hline(y=92, line_dash="dash", line_color="#ff4444", annotation_text="Critical")

    bp_fig = go.Figure(layout=chart_layout)
    bp_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["systolic"],
                                mode="lines", name="Systolic", line=dict(color="#00d4ff", width=1.5)))
    bp_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["diastolic"],
                                mode="lines", name="Diastolic", line=dict(color="#aa88ff", width=1.5)))
    bp_fig.update_layout(title="Blood Pressure (mmHg)")

    temp_fig = go.Figure(layout=chart_layout)
    temp_fig.add_trace(go.Scatter(x=df["timestamp"], y=df["temperature"],
                                  mode="lines", line=dict(color="#aa88ff", width=1.5),
                                  fill="tozeroy", fillcolor="rgba(170,136,255,0.1)"))
    temp_fig.update_layout(title="Temperature (°C)")
    temp_fig.add_hline(y=39.5, line_dash="dash", line_color="#ff4444", annotation_text="Fever")

    county_fig = go.Figure(layout=chart_layout)
    if not isinstance(county_df, dict) and not county_df.empty:
        county_fig.add_trace(go.Bar(
            x=county_df["county"], y=county_df["readings"],
            marker_color="#00d4ff", name="Readings"
        ))
        county_fig.add_trace(go.Bar(
            x=county_df["county"], y=county_df["critical"],
            marker_color="#ff4444", name="Critical"
        ))
    county_fig.update_layout(title="Readings by County", barmode="group")

    alert_rows = []
    if not alerts_df.empty:
        for _, row in alerts_df.iterrows():
            alert_rows.append(html.Div(style={
                "backgroundColor": "#2a0a0a", "padding": "8px 12px",
                "borderRadius": "4px", "marginBottom": "6px",
                "borderLeft": "3px solid #ff4444", "fontSize": "12px"
            }, children=[
                html.Span(f"{row['time']} | {row['patient_id']} | {row['hospital']}",
                          style={"color": "#ff8888", "display": "block"}),
                html.Span(row["alert"], style={"color": "#ffcccc"})
            ]))

    return kpis, hr_fig, spo2_fig, bp_fig, temp_fig, county_fig, alert_rows


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
