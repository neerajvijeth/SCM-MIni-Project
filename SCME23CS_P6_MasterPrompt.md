# SCME P6 — Supplier Relationship Management
## Complete Project Build Prompt (Paste directly into Claude Opus)

---

> **ROLE:** You are a senior full-stack data engineer and supply chain analyst.
> Build a complete, submission-ready academic project for course **UE23CS342BA1 — Supply Chain Management for Engineers**, **Problem Statement P6: Supplier Relationship Management**, PES University, Jan–May 2026.
> **Deadline: 20 April 2026.**
> Use **Python only** for all code (Plotly Dash for dashboard, scikit-learn/statsmodels for ML, SQLite for database). No Power BI or Tableau.

---

## PROBLEM STATEMENT — P6

> Inefficient supplier relationship management, characterized by a lack of collaboration tools,
> material and performance tracking, leads to communication and goods receipt delays,
> increased risk, and missed cost-optimization opportunities due to inconsistent supplier
> quality and unreliable lead times.

**SCM Areas addressed:** Supplier Performance Tracking · Procurement Reliability ·
Communication SLA Monitoring · Quality Inspection Management · Contract Compliance

---

## VERIFIED KPIs (Do not change these — they are domain-correct for SRM)

| # | KPI | Formula | Why it matters for P6 |
|---|-----|---------|----------------------|
| 1 | On-Time Delivery Rate (%) | (POs delivered on or before expected_delivery / Total delivered POs) × 100 | Core SRM metric — measures supplier reliability |
| 2 | Average Lead Time (days) | Mean of (actual_delivery_date − order_date) for all completed POs | Tracks procurement cycle efficiency |
| 3 | Lead Time Variance (days) | Std deviation of lead time per supplier | Inconsistent lead times = planning risk |
| 4 | Defect / Rejection Rate (%) | (Receipts with inspection_result = 'Fail' / Total inspections) × 100 | Measures supplier quality consistency |
| 5 | Supplier Performance Score (0–100) | Weighted: On-Time%(30) + Quality%(30) + Responsiveness%(20) + Cost Compliance%(20) | Single composite score for executive view |
| 6 | Cost Variance (%) | ((actual unit_price − contract baseline price) / contract baseline price) × 100 | Identifies cost overruns vs contracted rates |
| 7 | Communication Response Time (hrs) | Mean of response_time_hours across all communications per supplier | Measures supplier responsiveness |
| 8 | SLA Breach Count | COUNT of POs where actual_delivery > expected_delivery | Tracks contractual SLA violations |
| 9 | PO Fulfillment Rate (%) | (received_quantity / ordered_quantity) × 100 per PO | Detects short-shipment and partial delivery |
| 10 | Contracts Expiring in ≤ 30 Days | COUNT of contracts where end_date BETWEEN today AND today+30 | Risk alert for procurement continuity |
| 11 | Open / Pending POs | COUNT of POs with status = 'Pending' | Procurement backlog visibility |
| 12 | Unresolved Communications (>48 hrs) | COUNT of communications where resolved='No' AND response_time_hours > 48 | Communication bottleneck metric |

---

## DELIVERABLE 1 — Problem Statement Analysis

Write a structured 2-page analysis document (markdown format) with these exact sections:

### 1.1 Scope Definition
Cover these specific SRM sub-problems being addressed:
- Lack of a unified supplier performance tracking system
- No real-time visibility into goods receipt status and quality inspection outcomes
- Manual, untracked supplier communications leading to SLA breaches
- No predictive capability for lead times causing reactive procurement
- Absence of risk scoring to prioritise high-risk supplier relationships
- Contract expiry tracking done manually, leading to lapses

### 1.2 Business Impact (with realistic numbers)
Quantify each pain point:
- **Delivery delays:** Average 2–4 days of unplanned delay per order adds 8–12% to carrying cost
- **Quality defects:** A 5% average defect rate across suppliers increases rework/replacement cost by ~15% of procurement budget
- **Communication delays:** Response times exceeding 48 hours cause average 3-day procurement cycle extension
- **Lead time unpredictability:** ±30% lead time variance forces safety stock 20–25% higher than necessary
- **Contract lapses:** Each unmanaged contract expiry creates 2–4 weeks of emergency procurement at spot-market rates (typically 18–22% premium)
- **Supplier risk blindspot:** Without risk scoring, 1 in 5 supplier relationships is statistically at high risk of disruption at any given time (industry benchmark)

### 1.3 Proposed Solution
Describe: a Python-based interactive dashboard backed by a SQLite relational database, with three integrated ML models (lead time forecasting, supplier risk classification, anomaly detection on goods receipts). All built with Plotly Dash, pandas, scikit-learn, and statsmodels.

### 1.4 SCM Area Mapping
Map P6 explicitly to:
- **Procurement Management** — PO tracking, fulfillment rates, cost variance
- **Supplier Evaluation & Scorecard** — Performance score, risk classification
- **Inventory Quality Control** — Defect rate, inspection results, anomaly flags
- **Vendor Communication Management** — Response SLA, unresolved queries
- **Contract Lifecycle Management** — Expiry alerts, SLA breach tracking

---

## DELIVERABLE 2A — Database Schema (SQL DDL)

Create a file called `schema.sql` with the following exact schema.
All foreign keys must be enforced. Include comments on each table.

```sql
-- Table 1: Suppliers (master entity)
CREATE TABLE Suppliers (
    supplier_id     TEXT PRIMARY KEY,          -- e.g. SUP001
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,             -- Raw Materials | Packaging | Electronics | Logistics | MRO
    country         TEXT NOT NULL,
    city            TEXT,
    contact_email   TEXT,
    contact_phone   TEXT,
    contract_start  DATE,
    contract_end    DATE,
    payment_terms   TEXT,                      -- Net30 | Net60 | Net90
    baseline_price_index REAL DEFAULT 100.0,  -- reference price index for cost variance calc
    is_active       INTEGER DEFAULT 1          -- 1=active, 0=inactive
);

-- Table 2: Purchase Orders
CREATE TABLE PurchaseOrders (
    po_id               TEXT PRIMARY KEY,       -- e.g. PO2024001
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    material_name       TEXT NOT NULL,
    category            TEXT,
    quantity            REAL NOT NULL,
    unit                TEXT DEFAULT 'units',
    unit_price          REAL NOT NULL,          -- actual price paid
    total_value         REAL,                   -- quantity * unit_price
    order_date          DATE NOT NULL,
    expected_delivery   DATE NOT NULL,
    actual_delivery     DATE,                   -- NULL if not yet delivered
    status              TEXT NOT NULL           -- Pending | Delivered | Delayed | Cancelled
        CHECK(status IN ('Pending','Delivered','Delayed','Cancelled')),
    delay_days          INTEGER GENERATED ALWAYS AS
        (CASE WHEN actual_delivery IS NOT NULL
              THEN CAST(julianday(actual_delivery) - julianday(expected_delivery) AS INTEGER)
              ELSE NULL END) VIRTUAL           -- positive = late
);

-- Table 3: Goods Receipts
CREATE TABLE GoodsReceipts (
    receipt_id          TEXT PRIMARY KEY,       -- e.g. GR2024001
    po_id               TEXT NOT NULL REFERENCES PurchaseOrders(po_id),
    received_date       DATE NOT NULL,
    received_quantity   REAL NOT NULL,
    condition           TEXT NOT NULL
        CHECK(condition IN ('Accepted','Rejected','Partial')),
    warehouse_location  TEXT,
    received_by         TEXT
);

-- Table 4: Quality Inspections
CREATE TABLE QualityInspections (
    inspection_id       TEXT PRIMARY KEY,       -- e.g. QI2024001
    receipt_id          TEXT NOT NULL REFERENCES GoodsReceipts(receipt_id),
    inspection_date     DATE NOT NULL,
    inspector_name      TEXT NOT NULL,
    defect_rate_pct     REAL NOT NULL           -- percentage 0.0–100.0
        CHECK(defect_rate_pct BETWEEN 0 AND 100),
    defect_type         TEXT,                   -- Dimensional | Surface | Functional | Missing | Other
    inspection_result   TEXT NOT NULL
        CHECK(inspection_result IN ('Pass','Fail','Conditional')),
    remarks             TEXT
);

-- Table 5: Communications
CREATE TABLE Communications (
    comm_id             TEXT PRIMARY KEY,       -- e.g. CM2024001
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    comm_date           DATE NOT NULL,
    channel             TEXT NOT NULL
        CHECK(channel IN ('Email','Call','Meeting','Portal')),
    subject             TEXT NOT NULL,
    priority            TEXT DEFAULT 'Normal'
        CHECK(priority IN ('Low','Normal','High','Critical')),
    response_time_hours REAL,                   -- NULL if unresolved
    resolved            TEXT NOT NULL DEFAULT 'No'
        CHECK(resolved IN ('Yes','No'))
);

-- Table 6: Contracts
CREATE TABLE Contracts (
    contract_id         TEXT PRIMARY KEY,       -- e.g. CT2024001
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    value_inr           REAL NOT NULL,          -- total contract value in INR
    sla_lead_time_days  INTEGER NOT NULL,       -- agreed max lead time in days
    sla_defect_limit_pct REAL DEFAULT 5.0,     -- agreed max defect rate
    penalty_clause      TEXT,                   -- description of penalty terms
    renewal_status      TEXT NOT NULL
        CHECK(renewal_status IN ('Active','Expired','Renewed','Under Review'))
);
```

---

## DELIVERABLE 2B — Sample Data Generator

Create a file called `generate_data.py`.

**Requirements:**
- 30 suppliers across 5 categories (6 per category): Raw Materials, Packaging, Electronics, Logistics, MRO
- Supplier countries: mix of India, China, Germany, USA, Vietnam, Japan
- 500 purchase orders spanning January 2023 to March 2026
- Corresponding goods receipts (one per delivered/delayed PO)
- Corresponding quality inspections (one per goods receipt)
- 400+ communication records
- 30 contracts (one per supplier, some expired, some expiring soon, some active)

**Mandatory data patterns to inject (these enable meaningful ML results):**
- **3 consistently bad suppliers** (supplier IDs: SUP007, SUP014, SUP021): defect rate 18–30%, delay rate 60–70%, response time 72–120 hours
- **2 excellent suppliers** (SUP001, SUP003): defect rate < 2%, on-time rate > 95%, response time < 4 hours
- **Seasonal demand spike** in July–September (Q3): 40% more POs than other quarters
- **3 contracts expiring within 30 days** of April 2026 (use end_date between 2026-04-10 and 2026-04-30)
- **1 supplier with improving trend** (SUP010): defect rate decreasing month-over-month from 12% in Jan 2023 to 3% in Mar 2026
- **Price drift on raw materials**: unit_price for Raw Materials category increases ~8% per year

**Output files:** `suppliers.csv`, `purchase_orders.csv`, `goods_receipts.csv`, `quality_inspections.csv`, `communications.csv`, `contracts.csv`, and `scm_p6.db` (SQLite with all tables populated)

Use `faker`, `numpy`, `pandas`, `random`, `sqlite3`. Set `random.seed(42)` for reproducibility.

---

## DELIVERABLE 2C — ERD (Mermaid diagram)

Create a file called `erd.md` containing a mermaid erDiagram with all 6 tables, key fields, and cardinality:

```
erDiagram
    Suppliers ||--o{ PurchaseOrders : "places"
    Suppliers ||--o{ Communications : "has"
    Suppliers ||--o{ Contracts : "governed by"
    PurchaseOrders ||--o| GoodsReceipts : "fulfilled by"
    GoodsReceipts ||--o| QualityInspections : "inspected in"

    Suppliers {
        text supplier_id PK
        text name
        text category
        text country
        date contract_start
        date contract_end
        real baseline_price_index
    }
    PurchaseOrders {
        text po_id PK
        text supplier_id FK
        text material_name
        real quantity
        real unit_price
        date order_date
        date expected_delivery
        date actual_delivery
        text status
    }
    GoodsReceipts {
        text receipt_id PK
        text po_id FK
        date received_date
        real received_quantity
        text condition
    }
    QualityInspections {
        text inspection_id PK
        text receipt_id FK
        date inspection_date
        real defect_rate_pct
        text inspection_result
    }
    Communications {
        text comm_id PK
        text supplier_id FK
        date comm_date
        text channel
        real response_time_hours
        text resolved
    }
    Contracts {
        text contract_id PK
        text supplier_id FK
        date end_date
        integer sla_lead_time_days
        real sla_defect_limit_pct
        text renewal_status
    }
```

---

## DELIVERABLE 3 — Machine Learning Models

Create a file called `models.py`.

### Model 1 — Lead Time Forecasting (Regression)

**Goal:** Predict how many days a PO will take from order to delivery.

**Input features:**
- `supplier_id` (label-encoded)
- `category` (one-hot encoded: Raw Materials, Packaging, Electronics, Logistics, MRO)
- `quantity` (numeric)
- `unit_price` (numeric)
- `month` (1–12, extracted from order_date)
- `quarter` (1–4)
- `historical_avg_lead_time` (per supplier, computed from past POs)
- `historical_delay_rate` (per supplier, % of past POs that were delayed)

**Target variable:** `actual_lead_time_days` = actual_delivery − order_date (integer days)

**Pipeline:**
1. Baseline: Linear Regression — compute RMSE and R²
2. Main model: Random Forest Regressor (n_estimators=100, random_state=42) — compute RMSE, MAE, R²
3. Time series for top 5 suppliers: use `statsmodels` ARIMA(2,1,2) on monthly average lead time; forecast next 3 months with 95% confidence interval
4. Save: `model1_rf.pkl` (Random Forest), `model1_arima_results.pkl` dict keyed by supplier_id
5. Save predictions to `lead_time_predictions.csv` with columns: supplier_id, month, predicted_lead_time_days, lower_95, upper_95

**Print:** RMSE comparison table (Linear Regression vs Random Forest), Feature importance bar chart saved as `feature_importance.png`

---

### Model 2 — Supplier Risk Scoring (Classification)

**Goal:** Classify each supplier as Low / Medium / High risk and produce a 0–100 risk score.

**Feature engineering per supplier (aggregate from DB):**
- `on_time_rate` = % POs delivered on time (higher = better)
- `avg_defect_rate` = mean defect_rate_pct from QualityInspections (lower = better)
- `avg_lead_time_days` = mean lead time (lower = better)
- `lead_time_variance` = std of lead time (lower = better)
- `response_time_avg_hours` = mean response_time_hours from Communications (lower = better)
- `sla_breach_count` = count of POs where actual_delivery > expected_delivery (lower = better)
- `po_fulfillment_rate` = mean received_quantity / ordered_quantity (higher = better)
- `contract_compliance` = 1 if renewal_status='Active' and no breaches, else 0

**Label derivation (rule-based, before ML):**
- `High` risk: on_time_rate < 70% OR avg_defect_rate > 10% OR sla_breach_count > 5
- `Low` risk: on_time_rate > 90% AND avg_defect_rate < 3% AND sla_breach_count <= 1
- `Medium` risk: everything else

**Risk score (0–100):** Compute as weighted penalty score:
```
risk_score = 100 - (
    on_time_rate * 0.30 +
    (100 - avg_defect_rate * 5) * 0.30 +
    max(0, 100 - response_time_avg_hours * 0.5) * 0.20 +
    po_fulfillment_rate * 0.20
)
risk_score = clip(risk_score, 0, 100)
```
(Higher score = more risky)

**ML Model:** Random Forest Classifier (n_estimators=200, random_state=42) on the 8 features above predicting the 3-class label.
- Split 80/20, stratified
- Report: accuracy, weighted F1, confusion matrix
- Save: `model2_risk_classifier.pkl`
- Save: `supplier_risk_scores.csv` with columns: supplier_id, name, category, on_time_rate, avg_defect_rate, risk_score, risk_label, predicted_label

---

### Model 3 — Anomaly Detection on Goods Receipts

**Goal:** Flag goods receipts that are statistically anomalous — potential quality collapse, fraud, or data entry errors.

**Features per receipt (join GoodsReceipts + QualityInspections + PurchaseOrders):**
- `defect_rate_pct` (from QualityInspections)
- `fulfillment_ratio` = received_quantity / ordered_quantity
- `delivery_delay_days` = received_date − expected_delivery (from PurchaseOrders)
- `unit_price_vs_baseline` = (unit_price − supplier baseline_price_index) / baseline_price_index

**Algorithm:** Isolation Forest (contamination=0.05, random_state=42)
- Fit on all 4 features
- Produce: `anomaly_score` (the negative decision function output; higher = more anomalous)
- `is_anomaly` flag: 1 = anomalous, 0 = normal
- Save: `model3_isoforest.pkl`
- Save: `anomaly_flags.csv` with columns: receipt_id, po_id, supplier_id, supplier_name, received_date, defect_rate_pct, fulfillment_ratio, delivery_delay_days, anomaly_score, is_anomaly

**Visualization:** Save a scatter plot (`anomaly_scatter.png`) — x-axis: delivery_delay_days, y-axis: defect_rate_pct, color: is_anomaly (red = anomaly, blue = normal), size: anomaly_score

**Print:** Count of anomalies detected, top 10 most anomalous receipts table

---

## DELIVERABLE 4 — Interactive Dashboard (app.py)

Create a file called `app.py` using **Plotly Dash + Dash Bootstrap Components**.

**Architecture:**
- Read all data from `scm_p6.db` at startup using `sqlite3` + `pandas`
- Load pre-computed CSVs: `supplier_risk_scores.csv`, `lead_time_predictions.csv`, `anomaly_flags.csv`
- Use `dcc.Tabs` for 5 pages
- Use `dash_bootstrap_components` (theme: FLATLY or COSMO)
- Global filters: Date range picker (applies to all PO-based charts) + Category dropdown

**Page 1 — Executive Overview**

KPI Cards (top row, 6 cards):
1. **Total Active Suppliers** — COUNT(supplier_id) WHERE is_active=1
2. **Overall On-Time Delivery %** — (Delivered POs with delay_days ≤ 0 / Total completed POs) × 100
3. **Average Lead Time (days)** — Mean of (actual_delivery − order_date) for completed POs
4. **Average Defect Rate %** — Mean of defect_rate_pct from QualityInspections
5. **Open POs** — COUNT of POs with status='Pending'
6. **Contracts Expiring ≤ 30 days** — COUNT of contracts with end_date within 30 days

Charts:
- **Bar chart:** Top 10 suppliers by On-Time Delivery Rate % (sorted descending, with a red dashed line at 85% benchmark)
- **Pie chart:** PO Status distribution (Pending / Delivered / Delayed / Cancelled) — use colors: green, blue, red, grey
- **Line chart:** Monthly PO count and total PO value (dual Y-axis) from Jan 2023 to Mar 2026
- **Horizontal bar chart:** Average lead time by supplier category (5 bars for 5 categories)

All charts update when the date range picker or category dropdown changes (use callbacks).

---

**Page 2 — Supplier Scorecard**

- **DataTable** (dash.dash_table): all suppliers with columns — Supplier Name, Category, Country, On-Time%, Defect Rate%, Avg Lead Time, Risk Score, Risk Label
  - Risk Label column: color-coded cell — green for Low, yellow for Medium, red for High
  - Sortable, filterable, paginated (10 rows per page)
- **Radar chart** (plotly go.Scatterpolar): appears when a supplier row is clicked — 5 axes: Delivery Reliability, Quality, Responsiveness, Cost Compliance, Fulfillment Rate. Normalize all axes to 0–100. Show selected supplier vs category average.
- **Bar chart:** Supplier Performance Score ranked (all suppliers, horizontal bars, colored by risk label)
- **Scatter plot:** On-Time Rate (x) vs Defect Rate (y), bubble size = total PO value, color = risk label. Quadrant lines at x=85%, y=5% to show good/bad zones with labels ("Champions", "Quality Risk", "Delivery Risk", "Critical").

---

**Page 3 — Lead Time & Forecasting**

- **Line chart:** Historical monthly average lead time for selected suppliers (multi-line, one line per supplier). Multi-select dropdown for supplier selection.
- **Forecast chart:** Next 3-month predicted lead time per supplier — show historical line + forecast extension with shaded 95% CI band (using `lead_time_predictions.csv`). Use dashed line for forecast portion.
- **Bar chart:** Lead time variance (std dev) by supplier — sorted descending. Red bars for suppliers with variance > 7 days (high unpredictability).
- **Box plot:** Lead time distribution by material category — 5 boxes side by side showing median, IQR, outliers.

---

**Page 4 — Quality & Goods Receipts**

- **Histogram:** Distribution of defect_rate_pct across all inspections (bins of 2%). Add vertical lines at 5% (acceptable limit) and 10% (critical threshold).
- **Scatter plot:** defect_rate_pct (y) vs delivery_delay_days (x), colored by supplier category. Points sized by quantity.
- **Heatmap:** Defect rate by Supplier (y-axis, top 15 worst) × Month (x-axis). Color scale: green→yellow→red.
- **Anomaly flag table:** All receipts where is_anomaly=1 from `anomaly_flags.csv`. Columns: Receipt ID, Supplier Name, Date, Defect Rate%, Fulfillment Ratio, Delay Days, Anomaly Score. Sorted by anomaly_score descending.
- **Donut chart:** Inspection result breakdown — Pass / Fail / Conditional counts.

---

**Page 5 — Communications & Contracts**

- **Bar chart:** Average response time (hours) per supplier — sorted descending, with a red dashed SLA line at 24 hours. Top 10 worst responders.
- **Gauge chart** (plotly go.Indicator): Overall SLA compliance % = (Communications with response_time_hours ≤ 24 / Total resolved) × 100. Target: 90%.
- **Pie chart:** Communication channel breakdown — Email / Call / Meeting / Portal.
- **Timeline / Gantt-style chart:** Active contracts for all suppliers — horizontal bars from start_date to end_date, colored by renewal_status. Add a vertical red line at today (April 2026). Contracts expiring within 30 days highlighted with an orange border.
- **Table:** Contracts expiring within 90 days — Supplier Name, Contract Value (INR), End Date, SLA Lead Time, Renewal Status. Alert styling for those within 30 days.
- **Bar chart:** SLA breach count per supplier (top 15) — sorted descending, colored red.

---

**Technical requirements for app.py:**
- `app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])`
- All DB queries wrapped in a helper function `query_db(sql, params=())` that opens and closes SQLite connection safely
- All callbacks use `@app.callback` with proper `Input`/`Output` — no global state mutation
- Date range filter: `dcc.DatePickerRange` with `min_date_allowed='2023-01-01'`, `max_date_allowed='2026-04-20'`, `start_date='2023-01-01'`, `end_date='2026-03-31'`
- Include `if __name__ == '__main__': app.run_server(debug=True, port=8050)`
- Add a `requirements.txt` with pinned versions

---

## DELIVERABLE 5 — Project Report (Markdown)

Create a file called `report.md` with all the following sections fully written out.

Use the file naming convention in the PDF name: `SCME23CS_P6_001-002-003-004.pdf`

Sections to write:

### Title Page
```
UE23CS342BA1 — Supply Chain Management for Engineers
Problem Statement P6: Supplier Relationship Management
PES University | Jan–May 2026
Team Members: [Name 1 — SRN], [Name 2 — SRN], [Name 3 — SRN], [Name 4 — SRN]
Professor: Prof. Raghu B.A. Rao | raghubarao@pes.edu
Submission Date: 20 April 2026
```

### Abstract (150 words)
Write a precise abstract covering: what problem P6 addresses, what was built (DB + dashboard + 3 ML models), key results (e.g., 93% risk classification accuracy, 2.3-day RMSE on lead time forecasting), and the business value delivered.

### Section 1 — Introduction
Background on global SRM challenges. Why SRM matters in modern supply chains. What this project's scope covers.

### Section 2 — Problem Statement Analysis
Full content from Deliverable 1 above.

### Section 3 — Data Design
- Table-by-table justification (why each table exists, what questions it answers)
- ERD description (in prose, referencing the mermaid diagram)
- Sample data generation methodology and intentional patterns injected
- Data quality assumptions

### Section 4 — Dashboard Design
- Justification for each KPI chosen (reference KPI table above)
- Page-by-page description of each dashboard page with description of every chart and what decision it enables
- Screenshots placeholder: `[Insert screenshot of Page X here]`
- Design decisions: why Plotly Dash was chosen, color coding conventions, filter strategy

### Section 5 — Machine Learning
For each model:
- Problem it solves
- Algorithm rationale (why this algorithm, not alternatives)
- Features and target
- Results (RMSE/accuracy/F1 — use realistic placeholder numbers: Model 1 RMSE ~2.3 days, Model 2 accuracy ~91%, Model 3 flags ~25 anomalies out of 500 receipts)
- Business impact: "With lead time forecasts, safety stock can be reduced by an estimated 18%, saving ₹X in holding costs per year"

### Section 6 — Insights and Findings
Write exactly 7 insights derived from the dashboard, for example:
1. SUP007, SUP014, and SUP021 account for 62% of all SLA breaches despite representing only 10% of supplier count.
2. Q3 demand spikes (July–September) increase average lead time by 4.2 days across all categories.
3. Electronics category has the highest defect rate (avg 9.8%) vs MRO (avg 2.1%).
4. 3 contracts expiring in April 2026 represent ₹4.2 Cr in annual procurement value — urgent renewal needed.
5. Email is the dominant communication channel (58%) but has the highest avg response time (31 hrs vs 8 hrs for Portal).
6. The Isolation Forest flagged 25 anomalous receipts; 18 of these were from the 3 high-risk suppliers.
7. SUP010 shows a statistically significant improvement trend — defect rate dropped from 12% to 3% over 3 years, validating the supplier development programme.

### Section 7 — Challenges and Learnings
At least 5 genuine challenges: data generation realism, handling NULL actual_delivery for open POs, ARIMA stationarity issues with short time series, Dash callback complexity with multiple linked filters, interpreting Isolation Forest scores.

### Section 8 — Future Work
1. Real-time ERP integration (SAP/Oracle) via API connectors
2. NLP sentiment analysis on supplier email communications using BERT
3. Blockchain-based contract traceability for immutable SLA records
4. Multi-criteria supplier selection using AHP (Analytic Hierarchy Process)

### Section 9 — References
1. https://www.thoughtspot.com/data-trends/dashboard/supply-chain-kpis-metrics-for-dashboard
2. https://supplychaindigital.com/logistics/seven-key-features-effective-supply-chain-dashboards-take-supply-chain
3. https://www.bizinfograph.com/blog/supply-chain-dashboard/
4. https://inforiver.com/blog/general/supply-chain-kpis-inforiver-charts-powerbi/
5. https://www.slideteam.net/blog/top-10-supply-chain-dashboard-examples-with-templates-and-samples
6. https://cashflowinventory.com/blog/demand-and-supply-planning-kpis/
7. https://www.linkedin.com/pulse/7-mini-case-studies-successful-supply-chain-cost-rob-o-byrne/
8. Chopra, S. & Meindl, P. (2021). *Supply Chain Management: Strategy, Planning, and Operation* (7th ed.). Pearson.
9. Monczka, R. et al. (2020). *Purchasing and Supply Chain Management* (7th ed.). Cengage.

### Appendix
- Full SQL DDL (from schema.sql)
- Key Python snippets from models.py (Model 2 risk score formula, Model 3 Isolation Forest fit)

---

## DELIVERABLE 6 — Presentation Outline

Create a file called `presentation_outline.md` with a 10-slide outline.

**Slide 1 — Title Slide**
- Title: Supplier Relationship Management Dashboard
- Sub: UE23CS342BA1 SCME | Problem Statement P6
- Team names and SRNs
- Date: April 2026

**Slide 2 — The Problem (Why SRM Fails)**
- Visual: Pain-point infographic with 5 bullet stats from Section 1.2
- Key message: "Without data-driven SRM, companies overpay, over-stock, and over-react"

**Slide 3 — Our Solution Architecture**
- Visual: Simple flow diagram — Raw Data (6 tables) → SQLite DB → Python ETL → ML Models + Plotly Dash → Executive Dashboard
- Mention: 30 suppliers, 500+ POs, 3 ML models, 5-page dashboard

**Slide 4 — Database Schema**
- Visual: ERD screenshot (mermaid rendered)
- Highlight: 6 tables, key relationships, designed to answer 12 KPIs

**Slide 5 — Dashboard: Executive Overview**
- Screenshot of Page 1
- Point out: 6 KPI cards, on-time delivery bar chart, PO status pie chart

**Slide 6 — Dashboard: Supplier Scorecard**
- Screenshot of Page 2 scorecard table + radar chart
- Point out: Risk color coding, radar chart comparison, bubble scatter quadrants

**Slide 7 — ML Model 1: Lead Time Forecasting**
- Show: RMSE comparison table (LR vs RF), feature importance chart
- Show: Forecast line chart with confidence interval for 1 sample supplier
- Business value: "18% safety stock reduction possible"

**Slide 8 — ML Model 2: Supplier Risk Scoring**
- Show: Confusion matrix heatmap
- Show: Top 5 high-risk vs low-risk suppliers bar chart
- Business value: "Proactively identify at-risk suppliers before disruption occurs"

**Slide 9 — ML Model 3: Anomaly Detection**
- Show: Scatter plot (delay days vs defect rate, red=anomaly)
- Show: Anomaly flags table top 5 rows
- Business value: "25 suspicious receipts flagged — ₹X in potential fraud/quality loss"

**Slide 10 — Key Insights + Future Work**
- List 4 top insights (from Section 6)
- Future work: ERP integration, NLP on emails, Blockchain contracts
- Closing: "Data-driven SRM reduces procurement risk, cuts costs, and builds supplier trust"

---

## OUTPUT ORDER AND FILE LIST

Produce all files in this exact order:

1. `schema.sql` — complete DDL
2. `generate_data.py` — complete data generation script
3. `models.py` — all 3 ML models in one file, runnable in sequence
4. `app.py` — complete Plotly Dash application
5. `requirements.txt` — all Python dependencies with versions
6. `erd.md` — mermaid ERD
7. `report.md` — full academic report
8. `presentation_outline.md` — 10-slide outline

**Run order after generation:**
```bash
pip install -r requirements.txt
python generate_data.py      # creates scm_p6.db and all CSVs
python models.py             # trains models, saves .pkl files and prediction CSVs
python app.py                # launches dashboard at http://localhost:8050
```

---

## IMPORTANT CONSTRAINTS (Do not violate these)

1. **No placeholders.** Every function, callback, chart, and SQL query must be fully written and runnable.
2. **No Power BI or Tableau.** Python only — Plotly Dash for dashboard, matplotlib/seaborn only for saved .png charts from models.py.
3. **SQLite only** for the database — no PostgreSQL setup required. Use `sqlite3` built-in library.
4. **All Dash callbacks must be complete** — Input/Output/State specified, callback function body written, no `pass` stubs.
5. **random.seed(42)** in generate_data.py for reproducibility — the same data must regenerate identically every run.
6. **KPIs must use the exact formulas** defined in the KPI table above — do not invent alternative definitions.
7. **Anomaly detection contamination = 0.05** (5% of receipts flagged) — do not change this parameter.
8. **report.md** must have every section written out in full prose — no bullet-only sections.
9. If output is cut off, the user will say "continue" — resume from exactly where you stopped, do not restart.

---

*End of prompt. Begin with `schema.sql` immediately.*
