# SCM P6 End-to-End Project Explanation

## 1) Project Context

This project solves **Problem Statement P6: Supplier Relationship Management (SRM)** from SCM coursework.  
Main goal: build a practical system that helps managers monitor suppliers, detect issues early, and make data-driven decisions.

The project combines:
- Structured SCM data model (SQLite + CSVs)
- Machine learning for prediction and risk intelligence
- Interactive dashboard (Dash) for executive and operational views

---

## 2) Business Problem Being Solved

Many supply chains face these SRM issues:
- Inconsistent supplier delivery performance
- Defect-prone inbound material quality
- Slow supplier communication and SLA breaches
- Poor visibility into contract expiry and compliance
- Reactive planning due to unknown future lead times

This system addresses those gaps by providing:
- unified supplier performance view
- risk ranking of suppliers
- lead-time forecasting
- anomaly detection in goods receipts
- communication and contract monitoring

---

## 3) End-to-End Architecture

## 3.1 Data Layer
- **Database:** `scm_p6.db` (SQLite)
- **Schema:** `schema.sql`
- **ER notes:** `erd.md`

Core entities:
- `Suppliers`
- `PurchaseOrders`
- `GoodsReceipts`
- `QualityInspections`
- `Communications`
- `Contracts`

## 3.2 Data Generation Layer
- Script: `generate_data.py`
- Creates realistic synthetic data with seeded randomness for reproducibility.
- Exports:
  - `suppliers.csv`
  - `purchase_orders.csv`
  - `goods_receipts.csv`
  - `quality_inspections.csv`
  - `communications.csv`
  - `contracts.csv`
  - and populates `scm_p6.db`

Embedded realism patterns include:
- bad suppliers, good suppliers, one improving supplier
- Q3 demand spike pattern
- delay/defect behavior by supplier profile
- contract renewal and near-expiry scenarios

## 3.3 ML Layer
- Script: `models.py`
- Trains 3 models and saves outputs:
  - `model1_rf.pkl` + `model1_arima_results.pkl`
  - `model2_risk_classifier.pkl`
  - `model3_isoforest.pkl`
  - `lead_time_predictions.csv`
  - `supplier_risk_scores.csv`
  - `anomaly_flags.csv`
  - `model_metrics.json` (reproducible metric summary)

## 3.4 Visualization Layer
- App: `app.py` (Plotly Dash + Bootstrap)
- UI styling: `assets/dashboard.css`
- 5 tabs:
  - Executive Overview
  - Supplier Scorecard
  - Lead Time & Forecasting
  - Quality & Goods Receipts
  - Communications & Contracts

---

## 4) ML Models and Why They Are Used

## Model 1: Lead Time Forecasting
- Type: Regression + time series forecast
- Purpose: predict supplier lead times for planning and buffer decisions
- Output usage:
  - historical and predicted lead-time trends
  - feature-importance interpretation

## Model 2: Supplier Risk Classification
- Type: Classification
- Purpose: classify suppliers into risk bands (High/Medium/Low)
- Features include:
  - on-time rate
  - defect rate
  - response times
  - SLA breach count
  - fulfillment behavior
- Output usage:
  - supplier scorecard table
  - risk ranking and prioritization

## Model 3: Goods Receipt Anomaly Detection
- Type: Unsupervised anomaly detection
- Purpose: flag unusual receipts for quality/procurement review
- Output usage:
  - anomaly table and visual support for exception handling

---

## 5) How Data Flows Through the Project

1. `generate_data.py` creates SCM datasets and DB  
2. `models.py` reads DB, trains models, writes ML outputs  
3. `app.py` loads DB + ML output files  
4. Dashboard callbacks filter and aggregate data based on user selections  
5. Managers view KPIs/charts/tables and take action

---

## 6) Dashboard Decision Value by Page

## Executive Overview
- Fast top-level health check (on-time %, open POs, delays, defects, etc.)

## Supplier Scorecard
- Compare suppliers by performance and risk
- Identify top underperformers for corrective action

## Lead Time & Forecasting
- Understand lead-time trends and future risk windows
- Support procurement scheduling decisions

## Quality & Goods Receipts
- Monitor defect behavior and flagged anomalies
- Prioritize quality investigations

## Communications & Contracts
- Track response SLAs and contract expiry risks
- Prevent unmanaged contract lapses

---

## 7) Validation and Current Reliability Status

The project has been checked for core consistency:
- completed POs align with goods receipts and inspections
- relationship links are clean
- non-positive lead-time issue fixed
- model outputs align with dashboard values
- script stability improved for Windows terminal behavior

This makes the system suitable for academic demonstration and report submission.

---

## 8) How to Run the Full Project

From project root:

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Generate data and DB
```bash
python generate_data.py
```

3. Train models and create ML outputs
```bash
python models.py
```

4. Start dashboard
```bash
python app.py
```

5. Open:
`http://127.0.0.1:8050/`

---

## 9) Key Files at a Glance

- `generate_data.py`: synthetic SCM data generation
- `models.py`: ML training and output generation
- `app.py`: dashboard UI and callbacks
- `schema.sql`: relational schema
- `scm_p6.db`: runtime database
- `model_metrics.json`: latest model metric snapshot
- `report.md`: detailed academic report
- `presentation_outline.md`: final presentation flow

---

## 10) Final Summary

This project is an end-to-end SRM analytics solution that starts from structured data design, applies ML for predictive and risk insights, and delivers a management-ready interactive dashboard. It demonstrates practical SCM decision support across supplier performance, lead-time reliability, quality control, communication effectiveness, and contract governance.
