from datetime import datetime
from functools import lru_cache
from pathlib import Path
import json

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="SCM P6 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def load_data():
    purchase_orders = pd.read_csv(BASE_DIR / "purchase_orders.csv")
    suppliers = pd.read_csv(BASE_DIR / "suppliers.csv")
    risk_scores = pd.read_csv(BASE_DIR / "supplier_risk_scores.csv")
    anomalies = pd.read_csv(BASE_DIR / "anomaly_flags.csv")
    lead_preds = pd.read_csv(BASE_DIR / "lead_time_predictions.csv")
    with open(BASE_DIR / "model_metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    purchase_orders["order_date"] = pd.to_datetime(purchase_orders["order_date"], errors="coerce")
    purchase_orders["expected_delivery"] = pd.to_datetime(purchase_orders["expected_delivery"], errors="coerce")
    purchase_orders["actual_delivery"] = pd.to_datetime(purchase_orders["actual_delivery"], errors="coerce")
    anomalies["received_date"] = pd.to_datetime(anomalies["received_date"], errors="coerce")

    return {
        "purchase_orders": purchase_orders,
        "suppliers": suppliers,
        "risk_scores": risk_scores,
        "anomalies": anomalies,
        "lead_preds": lead_preds,
        "metrics": metrics,
    }


def _kpi_summary():
    data = load_data()
    po = data["purchase_orders"]
    suppliers = data["suppliers"]
    anomalies = data["anomalies"]

    completed = po[po["status"].isin(["Delivered", "Delayed"])].copy()
    on_time = (
        (completed["actual_delivery"].notna()) & (completed["actual_delivery"] <= completed["expected_delivery"])
    ).sum()
    on_time_pct = round((on_time / max(len(completed), 1)) * 100, 2)

    completed["lead_time_days"] = (completed["actual_delivery"] - completed["order_date"]).dt.days
    avg_lead_time = round(float(completed["lead_time_days"].dropna().mean()), 2) if not completed.empty else 0.0

    open_pos = int((po["status"] == "Pending").sum())
    active_suppliers = int((suppliers["is_active"] == 1).sum())
    delayed_count = int((po["status"] == "Delayed").sum())
    anomaly_count = int(anomalies["is_anomaly"].sum())

    return {
        "active_suppliers": active_suppliers,
        "completed_purchase_orders": int(len(completed)),
        "on_time_delivery_pct": on_time_pct,
        "average_lead_time_days": avg_lead_time,
        "open_purchase_orders": open_pos,
        "delayed_orders": delayed_count,
        "anomaly_count": anomaly_count,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/summary")
def summary():
    return _kpi_summary()


@app.get("/api/risk-suppliers")
def risk_suppliers(limit: int = Query(default=10, ge=1, le=100)):
    df = load_data()["risk_scores"].copy()
    cols = [
        "supplier_id",
        "name",
        "category",
        "on_time_rate",
        "avg_defect_rate",
        "risk_score",
        "predicted_label",
    ]
    out = df[cols].sort_values("risk_score", ascending=False).head(limit)
    return out.to_dict(orient="records")


@app.get("/api/anomalies")
def anomalies(limit: int = Query(default=15, ge=1, le=100)):
    df = load_data()["anomalies"].copy()
    cols = [
        "receipt_id",
        "supplier_name",
        "received_date",
        "defect_rate_pct",
        "delivery_delay_days",
        "anomaly_score",
        "is_anomaly",
    ]
    out = df[df["is_anomaly"] == 1][cols].sort_values("anomaly_score", ascending=False).head(limit)
    out["received_date"] = out["received_date"].dt.strftime("%Y-%m-%d")
    return out.to_dict(orient="records")


@app.get("/api/leadtime-forecast")
def leadtime_forecast():
    df = load_data()["lead_preds"].copy()
    return df.sort_values(["supplier_id", "month"]).to_dict(orient="records")


@app.get("/api/model-metrics")
def model_metrics():
    return load_data()["metrics"]


@app.post("/api/reload")
def reload_data():
    load_data.cache_clear()
    load_data()
    return {"reloaded": True}
