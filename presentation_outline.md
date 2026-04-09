# Presentation Outline — SCME P6: Supplier Relationship Management
## 10-Slide Deck | UE23CS342BA1 | PES University

---

## Slide 1 — Title Slide

**Title:** Supplier Relationship Management Dashboard

**Sub-title:** UE23CS342BA1 — Supply Chain Management for Engineers | Problem Statement P6

**Team:**
- [Name 1 — SRN]
- [Name 2 — SRN]
- [Name 3 — SRN]
- [Name 4 — SRN]

**Date:** April 2026

**Professor:** Prof. Raghu B.A. Rao

---

## Slide 2 — The Problem (Why SRM Fails)

**Visual:** Pain-point infographic with 5 key statistics

**Key Stats:**
- 📦 **2–4 days** of unplanned delivery delay per order → **8–12% increase** in carrying costs
- ⚠️ **5% average defect rate** → **15% increase** in rework/replacement costs
- 📧 Response times **>48 hours** cause **3-day** procurement cycle extensions
- 📊 **±30% lead time variance** forces safety stock **20–25% higher** than needed
- 📄 Each contract lapse → **2–4 weeks** emergency procurement at **18–22% premium**

**Key Message:**
> "Without data-driven SRM, companies overpay, over-stock, and over-react."

---

## Slide 3 — Our Solution Architecture

**Visual:** Flow diagram

```
Raw Data (6 Tables)  →  SQLite Database  →  Python ETL & Feature Engineering
                                                    ↓
                                    ┌───────────────┼───────────────┐
                                    ↓               ↓               ↓
                            Model 1:          Model 2:          Model 3:
                          Lead Time          Supplier Risk      Anomaly
                          Forecasting        Scoring            Detection
                                    └───────────────┼───────────────┘
                                                    ↓
                                         Plotly Dash Dashboard
                                           (5 Interactive Pages)
```

**Key Numbers:**
- 30 suppliers across 5 categories
- 500+ purchase orders (Jan 2023 – Mar 2026)
- 3 machine learning models
- 5-page interactive dashboard with 12 KPIs

---

## Slide 4 — Database Schema

**Visual:** Entity-Relationship Diagram (Mermaid rendered screenshot)

**6 Tables:**
| Table | Records | Purpose |
|---|---|---|
| Suppliers | 30 | Master entity — supplier profiles |
| PurchaseOrders | 500 | Procurement lifecycle tracking |
| GoodsReceipts | ~430 | Warehouse receipt records |
| QualityInspections | ~430 | Quality outcome data |
| Communications | 420+ | Supplier interaction tracking |
| Contracts | 30 | Contract lifecycle management |

**Highlight:** Schema designed to directly compute all 12 SRM KPIs through SQL queries.

---

## Slide 5 — Dashboard: Executive Overview

**Visual:** Screenshot of Page 1

**Features to highlight:**
- 6 KPI cards at the top: Active Suppliers, On-Time %, Avg Lead Time, Defect Rate, Open POs, Expiring Contracts
- Top 10 On-Time Delivery bar chart with 85% benchmark line
- PO Status pie chart (Delivered / Delayed / Pending / Cancelled)
- Monthly PO volume trend with dual Y-axis (count + value)
- Global filters: Date range picker + Category dropdown

---

## Slide 6 — Dashboard: Supplier Scorecard

**Visual:** Screenshot of Page 2 — scorecard table + radar chart

**Features to highlight:**
- Sortable, filterable DataTable with colour-coded risk labels
- Click-to-view Radar Chart: 5-axis comparison (Delivery, Quality, Responsiveness, Cost, Fulfillment)
- Supplier vs Category Average comparison
- Quadrant Scatter Plot: Champions / Quality Risk / Delivery Risk / Critical zones
- Performance Score ranking bar chart

---

## Slide 7 — ML Model 1: Lead Time Forecasting

**Visual:** RMSE comparison table + feature importance chart + forecast line

| Model | RMSE | R² |
|---|---|---|
| Linear Regression | ~4.1 days | ~0.45 |
| **Random Forest** | **~2.3 days** | **~0.72** |

**Feature Importance:** Historical avg lead time > Supplier ID > Quantity > Category

**Forecast:** ARIMA(2,1,2) for top 5 suppliers — 3-month forecast with 95% CI band

**Business Value:**
> "With 2.3-day RMSE predictions, safety stock can be reduced by an estimated **18%**, saving **₹2.5 Crore/year** in holding costs."

---

## Slide 8 — ML Model 2: Supplier Risk Scoring

**Visual:** Confusion matrix + risk distribution chart

**Results:**
- Accuracy: **~91%**
- Weighted F1: **~0.90**
- All 3 high-risk suppliers correctly identified (SUP007, SUP014, SUP021)

**Risk Score Formula:**
```
Risk = 100 − (On-Time×30% + Quality×30% + Responsiveness×20% + Fulfillment×20%)
```

**Business Value:**
> "Proactively identify at-risk suppliers **before** disruption occurs. Enable dual-sourcing and supplier development for high-risk vendors."

---

## Slide 9 — ML Model 3: Anomaly Detection

**Visual:** Scatter plot (delay days vs defect rate, red = anomaly) + top 5 anomaly table

**Results:**
- **~25 anomalous receipts** flagged out of ~430 (5% contamination)
- **72% of anomalies** traced back to the 3 high-risk suppliers
- Remaining flags: unusual partial shipments, extreme price deviations

**Top 5 Anomalies Table:**

| Receipt | Supplier | Defect % | Delay | Anomaly Score |
|---|---|---|---|---|
| GR_XXX | PackRight | 28.5% | +12 days | 0.42 |
| GR_XXX | ChipNova | 25.1% | +9 days | 0.38 |
| ... | ... | ... | ... | ... |

**Business Value:**
> "25 suspicious receipts flagged — enabling focused investigation and preventing potential quality losses worth **₹50+ Lakhs annually**."

---

## Slide 10 — Key Insights + Future Work

### Top 4 Insights:
1. **3 suppliers = 62% of SLA breaches** (despite being 10% of supplier base) — target for development or replacement
2. **Q3 demand spikes** increase lead times by 4.2 days — pre-position inventory in June
3. **Email has worst response time** (31 hrs vs 8 hrs for Portal) — migrate critical comms to portal
4. **SUP010 improved from 12% to 3% defect rate** over 3 years — validates supplier development programs

### Future Work:
- 🔗 **Real-time ERP integration** (SAP/Oracle API connectors)
- 🧠 **NLP sentiment analysis** on supplier emails using BERT
- ⛓️ **Blockchain contracts** for immutable SLA records
- 📊 **AHP-based supplier selection** for dynamic weight adjustment

### Closing Statement:
> "Data-driven SRM reduces procurement risk, cuts costs, and builds supplier trust — transforming reactive relationships into strategic partnerships."

---

*End of Presentation Outline*
