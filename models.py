"""
SCME P6 — Supplier Relationship Management
Machine Learning Models:
  Model 1: Lead Time Forecasting (Regression)
  Model 2: Supplier Risk Scoring (Classification)
  Model 3: Anomaly Detection on Goods Receipts (Isolation Forest)

Run: python models.py  (after running generate_data.py)
"""

import os
import warnings
import sqlite3
import pickle

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, f1_score, confusion_matrix, classification_report,
)
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scm_p6.db")


def query_db(sql, params=()):
    """Execute a SQL query and return a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


# ============================================================
# MODEL 1 — Lead Time Forecasting (Regression)
# ============================================================
def model1_lead_time_forecasting():
    print("\n" + "=" * 60)
    print("MODEL 1 — Lead Time Forecasting (Regression)")
    print("=" * 60)

    # Load completed POs (Delivered or Delayed — have actual_delivery)
    po_df = query_db("""
        SELECT po_id, supplier_id, category, quantity, unit_price,
               order_date, expected_delivery, actual_delivery, status
        FROM PurchaseOrders
        WHERE actual_delivery IS NOT NULL
          AND status IN ('Delivered', 'Delayed')
    """)

    po_df["order_date"] = pd.to_datetime(po_df["order_date"])
    po_df["actual_delivery"] = pd.to_datetime(po_df["actual_delivery"])
    po_df["actual_lead_time_days"] = (po_df["actual_delivery"] - po_df["order_date"]).dt.days
    po_df["month"] = po_df["order_date"].dt.month
    po_df["quarter"] = po_df["order_date"].dt.quarter

    # Filter out bad data
    po_df = po_df[po_df["actual_lead_time_days"] > 0].copy()

    # Compute historical features per supplier
    supplier_stats = po_df.groupby("supplier_id").agg(
        historical_avg_lead_time=("actual_lead_time_days", "mean"),
        total_pos=("po_id", "count"),
    ).reset_index()

    # Historical delay rate
    delayed_counts = po_df[po_df["status"] == "Delayed"].groupby("supplier_id")["po_id"].count().reset_index()
    delayed_counts.columns = ["supplier_id", "delayed_count"]
    supplier_stats = supplier_stats.merge(delayed_counts, on="supplier_id", how="left")
    supplier_stats["delayed_count"] = supplier_stats["delayed_count"].fillna(0)
    supplier_stats["historical_delay_rate"] = (
        supplier_stats["delayed_count"] / supplier_stats["total_pos"] * 100
    )

    po_df = po_df.merge(
        supplier_stats[["supplier_id", "historical_avg_lead_time", "historical_delay_rate"]],
        on="supplier_id",
        how="left",
    )

    # Feature engineering
    le_supplier = LabelEncoder()
    po_df["supplier_encoded"] = le_supplier.fit_transform(po_df["supplier_id"])

    # One-hot encode category
    category_dummies = pd.get_dummies(po_df["category"], prefix="cat")
    po_df = pd.concat([po_df, category_dummies], axis=1)

    feature_cols = (
        ["supplier_encoded", "quantity", "unit_price", "month", "quarter",
         "historical_avg_lead_time", "historical_delay_rate"]
        + [c for c in category_dummies.columns]
    )

    X = po_df[feature_cols].values
    y = po_df["actual_lead_time_days"].values

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Baseline: Linear Regression ---
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    r2_lr = r2_score(y_test, y_pred_lr)

    # --- Main Model: Random Forest Regressor ---
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)

    print("\n--- RMSE Comparison ---")
    print(f"{'Model':<25} {'RMSE':>8} {'R²':>8}")
    print("-" * 43)
    print(f"{'Linear Regression':<25} {rmse_lr:>8.2f} {r2_lr:>8.3f}")
    print(f"{'Random Forest':<25} {rmse_rf:>8.2f} {r2_rf:>8.3f}")
    print(f"\nRandom Forest MAE: {mae_rf:.2f} days")

    # Feature importance
    importances = rf.feature_importances_
    feature_names = (
        ["Supplier", "Quantity", "Unit Price", "Month", "Quarter",
         "Hist Avg Lead Time", "Hist Delay Rate"]
        + [c.replace("cat_", "") for c in category_dummies.columns]
    )

    fi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances,
    }).sort_values("Importance", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(fi_df["Feature"], fi_df["Importance"], color="#2196F3", edgecolor="white")
    ax.set_xlabel("Feature Importance", fontsize=12)
    ax.set_title("Model 1 — Random Forest Feature Importance (Lead Time Prediction)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(BASE_DIR, "feature_importance.png"), dpi=150)
    plt.close()
    print("\nSaved: feature_importance.png")

    # --- ARIMA Forecasting for Top 5 Suppliers ---
    print("\n--- ARIMA Forecasting (Top 5 Suppliers by PO count) ---")
    top5 = po_df.groupby("supplier_id")["po_id"].count().nlargest(5).index.tolist()

    arima_results = {}
    all_predictions = []

    for sid in top5:
        sid_data = po_df[po_df["supplier_id"] == sid].copy()
        sid_data["year_month"] = sid_data["order_date"].dt.to_period("M")
        monthly = sid_data.groupby("year_month")["actual_lead_time_days"].mean()
        monthly.index = monthly.index.to_timestamp()

        if len(monthly) < 12:
            print(f"  {sid}: Not enough data for ARIMA ({len(monthly)} months), skipping")
            continue

        # Resample to fill gaps
        monthly = monthly.resample("MS").mean().interpolate()

        try:
            model = ARIMA(monthly, order=(2, 1, 2))
            fitted = model.fit()

            # Forecast next 3 months
            forecast = fitted.get_forecast(steps=3)
            pred_mean = forecast.predicted_mean
            conf_int = forecast.conf_int(alpha=0.05)

            arima_results[sid] = {
                "historical": monthly,
                "forecast_mean": pred_mean,
                "conf_int": conf_int,
            }

            for i, (date, pred) in enumerate(pred_mean.items()):
                lower = conf_int.iloc[i, 0]
                upper = conf_int.iloc[i, 1]
                all_predictions.append({
                    "supplier_id": sid,
                    "month": date.strftime("%Y-%m-%d"),
                    "predicted_lead_time_days": round(pred, 2),
                    "lower_95": round(lower, 2),
                    "upper_95": round(upper, 2),
                })

            print(f"  {sid}: ARIMA(2,1,2) fit OK — AIC={fitted.aic:.1f}")
        except Exception as e:
            print(f"  {sid}: ARIMA failed — {e}")

    # Save models
    with open(os.path.join(BASE_DIR, "model1_rf.pkl"), "wb") as f:
        pickle.dump(rf, f)
    with open(os.path.join(BASE_DIR, "model1_arima_results.pkl"), "wb") as f:
        pickle.dump(arima_results, f)

    # Save predictions CSV
    pred_df = pd.DataFrame(all_predictions)
    pred_df.to_csv(os.path.join(BASE_DIR, "lead_time_predictions.csv"), index=False)
    print(f"\nSaved: model1_rf.pkl, model1_arima_results.pkl, lead_time_predictions.csv ({len(pred_df)} rows)")

    return rf, arima_results


# ============================================================
# MODEL 2 — Supplier Risk Scoring (Classification)
# ============================================================
def model2_risk_scoring():
    print("\n" + "=" * 60)
    print("MODEL 2 — Supplier Risk Scoring (Classification)")
    print("=" * 60)

    # --- Feature Engineering per Supplier ---
    suppliers = query_db("SELECT supplier_id, name, category FROM Suppliers WHERE is_active=1")

    # On-time rate
    po_df = query_db("""
        SELECT supplier_id, po_id, status, actual_delivery, expected_delivery,
               quantity, unit_price
        FROM PurchaseOrders
        WHERE status IN ('Delivered', 'Delayed')
    """)
    po_df["actual_delivery"] = pd.to_datetime(po_df["actual_delivery"])
    po_df["expected_delivery"] = pd.to_datetime(po_df["expected_delivery"])
    po_df["on_time"] = (po_df["actual_delivery"] <= po_df["expected_delivery"]).astype(int)
    po_df["lead_time"] = (po_df["actual_delivery"] - pd.to_datetime(
        query_db("SELECT po_id, order_date FROM PurchaseOrders").set_index("po_id").loc[po_df["po_id"].values, "order_date"].values
    )).dt.days

    # Recalculate lead time properly
    po_full = query_db("""
        SELECT po_id, supplier_id, order_date, actual_delivery, expected_delivery,
               quantity, status
        FROM PurchaseOrders
        WHERE actual_delivery IS NOT NULL AND status IN ('Delivered', 'Delayed')
    """)
    po_full["order_date"] = pd.to_datetime(po_full["order_date"])
    po_full["actual_delivery"] = pd.to_datetime(po_full["actual_delivery"])
    po_full["expected_delivery"] = pd.to_datetime(po_full["expected_delivery"])
    po_full["lead_time"] = (po_full["actual_delivery"] - po_full["order_date"]).dt.days
    po_full["on_time"] = (po_full["actual_delivery"] <= po_full["expected_delivery"]).astype(int)

    # SLA breach count
    po_full["sla_breach"] = (po_full["actual_delivery"] > po_full["expected_delivery"]).astype(int)

    supplier_po_stats = po_full.groupby("supplier_id").agg(
        on_time_rate=("on_time", lambda x: round(x.mean() * 100, 2)),
        avg_lead_time_days=("lead_time", "mean"),
        lead_time_variance=("lead_time", "std"),
        sla_breach_count=("sla_breach", "sum"),
    ).reset_index()
    supplier_po_stats["lead_time_variance"] = supplier_po_stats["lead_time_variance"].fillna(0)

    # Average defect rate
    inspections = query_db("""
        SELECT qi.inspection_id, qi.receipt_id, qi.defect_rate_pct,
               gr.po_id
        FROM QualityInspections qi
        JOIN GoodsReceipts gr ON qi.receipt_id = gr.receipt_id
    """)
    po_supplier_map = query_db("SELECT po_id, supplier_id FROM PurchaseOrders")
    inspections = inspections.merge(po_supplier_map, on="po_id", how="left")

    defect_stats = inspections.groupby("supplier_id").agg(
        avg_defect_rate=("defect_rate_pct", "mean"),
    ).reset_index()
    defect_stats["avg_defect_rate"] = defect_stats["avg_defect_rate"].round(2)

    # Response time avg
    comms = query_db("""
        SELECT supplier_id, response_time_hours
        FROM Communications
        WHERE resolved = 'Yes' AND response_time_hours IS NOT NULL
    """)
    comm_stats = comms.groupby("supplier_id").agg(
        response_time_avg_hours=("response_time_hours", "mean"),
    ).reset_index()
    comm_stats["response_time_avg_hours"] = comm_stats["response_time_avg_hours"].round(2)

    # PO fulfillment rate
    receipts = query_db("""
        SELECT gr.po_id, gr.received_quantity, po.quantity as ordered_quantity, po.supplier_id
        FROM GoodsReceipts gr
        JOIN PurchaseOrders po ON gr.po_id = po.po_id
    """)
    receipts["fulfillment"] = (receipts["received_quantity"] / receipts["ordered_quantity"] * 100).clip(0, 100)
    fulfill_stats = receipts.groupby("supplier_id").agg(
        po_fulfillment_rate=("fulfillment", "mean"),
    ).reset_index()
    fulfill_stats["po_fulfillment_rate"] = fulfill_stats["po_fulfillment_rate"].round(2)

    # Contract compliance
    contracts = query_db("""
        SELECT supplier_id, renewal_status
        FROM Contracts
    """)
    contracts["contract_compliance"] = (contracts["renewal_status"] == "Active").astype(int)
    contract_stats = contracts.groupby("supplier_id")["contract_compliance"].max().reset_index()

    # Merge all features
    features = suppliers.merge(supplier_po_stats, on="supplier_id", how="left")
    features = features.merge(defect_stats, on="supplier_id", how="left")
    features = features.merge(comm_stats, on="supplier_id", how="left")
    features = features.merge(fulfill_stats, on="supplier_id", how="left")
    features = features.merge(contract_stats, on="supplier_id", how="left")

    # Fill NaNs
    features = features.fillna({
        "on_time_rate": 50,
        "avg_lead_time_days": 15,
        "lead_time_variance": 5,
        "sla_breach_count": 0,
        "avg_defect_rate": 5,
        "response_time_avg_hours": 24,
        "po_fulfillment_rate": 90,
        "contract_compliance": 0,
    })

    # --- Rule-based Label Derivation ---
    def assign_risk_label(row):
        if row["on_time_rate"] < 70 or row["avg_defect_rate"] > 10 or row["sla_breach_count"] > 5:
            return "High"
        elif row["on_time_rate"] > 90 and row["avg_defect_rate"] < 3 and row["sla_breach_count"] <= 1:
            return "Low"
        else:
            return "Medium"

    features["risk_label"] = features.apply(assign_risk_label, axis=1)

    # --- Risk Score Calculation ---
    def compute_risk_score(row):
        score = 100 - (
            row["on_time_rate"] * 0.30  +
            (100 - row["avg_defect_rate"] * 5) * 0.30 +
            max(0, 100 - row["response_time_avg_hours"] * 0.5) * 0.20 +
            row["po_fulfillment_rate"] * 0.20
        )
        return round(np.clip(score, 0, 100), 2)

    features["risk_score"] = features.apply(compute_risk_score, axis=1)

    print(f"\nRisk Label Distribution:")
    print(features["risk_label"].value_counts().to_string())
    print(f"\nRisk Score Statistics:")
    print(features["risk_score"].describe().to_string())

    # --- ML Classification ---
    feature_cols = [
        "on_time_rate", "avg_defect_rate", "avg_lead_time_days",
        "lead_time_variance", "response_time_avg_hours",
        "sla_breach_count", "po_fulfillment_rate", "contract_compliance",
    ]

    X = features[feature_cols].values
    le_risk = LabelEncoder()
    y = le_risk.fit_transform(features["risk_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n--- Classification Results ---")
    print(f"Accuracy: {acc:.2%}")
    print(f"Weighted F1: {f1:.3f}")
    print(f"\nConfusion Matrix:")
    labels = le_risk.classes_
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df.to_string())
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=labels))

    # Predict on all suppliers
    y_pred_all = clf.predict(X)
    features["predicted_label"] = le_risk.inverse_transform(y_pred_all)

    # Save model
    with open(os.path.join(BASE_DIR, "model2_risk_classifier.pkl"), "wb") as f:
        pickle.dump(clf, f)

    # Save risk scores CSV
    output_cols = [
        "supplier_id", "name", "category", "on_time_rate", "avg_defect_rate",
        "risk_score", "risk_label", "predicted_label",
    ]
    features[output_cols].to_csv(
        os.path.join(BASE_DIR, "supplier_risk_scores.csv"), index=False
    )
    print(f"\nSaved: model2_risk_classifier.pkl, supplier_risk_scores.csv ({len(features)} rows)")

    return clf, features


# ============================================================
# MODEL 3 — Anomaly Detection on Goods Receipts
# ============================================================
def model3_anomaly_detection():
    print("\n" + "=" * 60)
    print("MODEL 3 — Anomaly Detection on Goods Receipts")
    print("=" * 60)

    # Join GoodsReceipts + QualityInspections + PurchaseOrders + Suppliers
    df = query_db("""
        SELECT
            gr.receipt_id,
            gr.po_id,
            gr.received_date,
            gr.received_quantity,
            qi.defect_rate_pct,
            po.supplier_id,
            po.quantity AS ordered_quantity,
            po.unit_price,
            po.expected_delivery,
            s.name AS supplier_name,
            s.baseline_price_index
        FROM GoodsReceipts gr
        JOIN QualityInspections qi ON gr.receipt_id = qi.receipt_id
        JOIN PurchaseOrders po ON gr.po_id = po.po_id
        JOIN Suppliers s ON po.supplier_id = s.supplier_id
    """)

    # Feature engineering
    df["fulfillment_ratio"] = (df["received_quantity"] / df["ordered_quantity"]).round(4)
    df["received_date"] = pd.to_datetime(df["received_date"])
    df["expected_delivery"] = pd.to_datetime(df["expected_delivery"])
    df["delivery_delay_days"] = (df["received_date"] - df["expected_delivery"]).dt.days
    df["unit_price_vs_baseline"] = (
        (df["unit_price"] - df["baseline_price_index"]) / df["baseline_price_index"]
    ).round(4)

    # Features for Isolation Forest
    feature_cols = ["defect_rate_pct", "fulfillment_ratio", "delivery_delay_days", "unit_price_vs_baseline"]
    X = df[feature_cols].values

    # Fit Isolation Forest
    iso = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
    labels = iso.fit_predict(X)
    scores = -iso.decision_function(X)  # Higher = more anomalous

    df["anomaly_score"] = scores.round(4)
    df["is_anomaly"] = (labels == -1).astype(int)

    anomaly_count = df["is_anomaly"].sum()
    total = len(df)
    print(f"\nTotal receipts analyzed: {total}")
    print(f"Anomalies detected: {anomaly_count} ({anomaly_count/total*100:.1f}%)")

    # Top 10 most anomalous
    top10 = df.nlargest(10, "anomaly_score")[
        ["receipt_id", "supplier_name", "received_date", "defect_rate_pct",
         "fulfillment_ratio", "delivery_delay_days", "anomaly_score", "is_anomaly"]
    ]
    print(f"\n--- Top 10 Most Anomalous Receipts ---")
    print(top10.to_string(index=False))

    # Scatter plot
    fig, ax = plt.subplots(figsize=(12, 8))
    normal = df[df["is_anomaly"] == 0]
    anomaly = df[df["is_anomaly"] == 1]

    ax.scatter(
        normal["delivery_delay_days"], normal["defect_rate_pct"],
        c="#2196F3", alpha=0.5, s=30, label="Normal", edgecolors="white", linewidths=0.5
    )
    ax.scatter(
        anomaly["delivery_delay_days"], anomaly["defect_rate_pct"],
        c="#F44336", alpha=0.8,
        s=anomaly["anomaly_score"] * 200 + 50,
        label="Anomaly", edgecolors="black", linewidths=1
    )
    ax.set_xlabel("Delivery Delay (days)", fontsize=12)
    ax.set_ylabel("Defect Rate (%)", fontsize=12)
    ax.set_title("Model 3 — Anomaly Detection: Delay vs Defect Rate", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.axhline(y=5, color="orange", linestyle="--", alpha=0.6, label="5% Defect Threshold")
    ax.axhline(y=10, color="red", linestyle="--", alpha=0.6, label="10% Critical Threshold")
    plt.tight_layout()
    fig.savefig(os.path.join(BASE_DIR, "anomaly_scatter.png"), dpi=150)
    plt.close()
    print("\nSaved: anomaly_scatter.png")

    # Save model
    with open(os.path.join(BASE_DIR, "model3_isoforest.pkl"), "wb") as f:
        pickle.dump(iso, f)

    # Save anomaly flags CSV
    output_cols = [
        "receipt_id", "po_id", "supplier_id", "supplier_name", "received_date",
        "defect_rate_pct", "fulfillment_ratio", "delivery_delay_days",
        "anomaly_score", "is_anomaly",
    ]
    df[output_cols].to_csv(os.path.join(BASE_DIR, "anomaly_flags.csv"), index=False)
    print(f"Saved: model3_isoforest.pkl, anomaly_flags.csv ({len(df)} rows)")

    return iso, df


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("SCME P6 — Training Machine Learning Models")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please run generate_data.py first.")
        return

    # Model 1
    rf_model, arima_results = model1_lead_time_forecasting()

    # Model 2
    risk_clf, risk_features = model2_risk_scoring()

    # Model 3
    iso_model, anomaly_df = model3_anomaly_detection()

    print("\n" + "=" * 60)
    print("All models trained and saved successfully!")
    print("=" * 60)
    print("\nOutput files:")
    for f in [
        "model1_rf.pkl", "model1_arima_results.pkl", "lead_time_predictions.csv",
        "feature_importance.png", "model2_risk_classifier.pkl",
        "supplier_risk_scores.csv", "model3_isoforest.pkl",
        "anomaly_flags.csv", "anomaly_scatter.png",
    ]:
        path = os.path.join(BASE_DIR, f)
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists} {f}")


if __name__ == "__main__":
    main()
