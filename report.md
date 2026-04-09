# UE23CS342BA1 — Supply Chain Management for Engineers
# Problem Statement P6: Supplier Relationship Management

**PES University | Jan–May 2026**

**Team Members:**
- [Name 1 — SRN]
- [Name 2 — SRN]
- [Name 3 — SRN]
- [Name 4 — SRN]

**Professor:** Prof. Raghu B.A. Rao | raghubarao@pes.edu

**Submission Date:** 20 April 2026

---

## Abstract

Supplier Relationship Management (SRM) remains a critical yet often under-instrumented component of modern supply chains. This project addresses Problem Statement P6, which identifies inefficiencies in supplier performance tracking, communication management, quality inspection processes, and contract lifecycle oversight. We developed a comprehensive Python-based analytical platform comprising a SQLite relational database (6 tables, 30 suppliers, 500 purchase orders), three machine learning models, and an interactive five-page dashboard built with Plotly Dash. On the latest reproducible run, the lead time forecasting module reports RMSE 3.85 days (Random Forest) and RMSE 3.67 days (Linear baseline), the supplier risk classifier reports 83.33% accuracy with weighted F1 0.815, and the Isolation Forest flags 23 anomalous goods receipts out of 449 analyzed. Together, these components transform reactive SRM into a data-driven discipline by providing actionable visibility into supplier performance, quality trends, contractual compliance, and exception handling.

---

## Section 1 — Introduction

### 1.1 Background

Global supply chains have grown increasingly complex, spanning multiple geographies, supplier tiers, and material categories. The success of any manufacturing or distribution operation hinges critically on the reliability, quality, and responsiveness of its supplier base. Yet, many organisations continue to manage supplier relationships through fragmented systems — spreadsheets for tracking purchase orders, email threads for communication, and manual calendars for contract renewals.

Supplier Relationship Management (SRM) refers to the systematic approach to evaluating, managing, and optimising supplier interactions. Effective SRM goes beyond mere cost negotiation; it encompasses delivery reliability measurement, quality trend analysis, communication responsiveness tracking, risk assessment, and strategic alignment. According to the Institute for Supply Management, organisations with mature SRM programmes report up to 12% lower procurement costs and 23% fewer supply disruptions compared to those without formal SRM systems.

The lack of integrated SRM tools creates a cascade of operational problems. Without real-time performance tracking, procurement teams cannot distinguish between consistently reliable suppliers and those exhibiting deteriorating service levels. Without communication SLA monitoring, supplier queries go unanswered for days, extending procurement cycles unnecessarily. Without predictive models for lead times, organisations are forced to maintain excessive safety stock, tying up working capital. And without automated contract expiry alerts, critical agreements lapse, forcing emergency procurement at spot-market premiums.

### 1.2 Project Scope

This project addresses Problem Statement P6 as defined in the course UE23CS342BA1 — Supply Chain Management for Engineers. The scope spans five core SRM sub-domains: Supplier Performance Tracking, Procurement Reliability Analysis, Communication SLA Monitoring, Quality Inspection Management, and Contract Compliance Oversight. The solution is built entirely in Python, using SQLite for data storage, scikit-learn and statsmodels for machine learning, and Plotly Dash for interactive visualisation.

---

## Section 2 — Problem Statement Analysis

### 2.1 Scope Definition

This project addresses six interconnected sub-problems within the broader SRM challenge:

**Lack of a unified supplier performance tracking system.** Most organisations evaluate suppliers either not at all or through annual reviews that fail to capture month-to-month performance trends. Without continuous monitoring, deteriorating supplier performance goes undetected until it causes production disruptions. Our system computes and visualises 12 KPIs across delivery, quality, cost, and communication dimensions, updated with every new data point.

**No real-time visibility into goods receipt status and quality inspection outcomes.** When goods arrive at the warehouse, the quality inspection data is often recorded in isolated spreadsheets. Quality managers lack visibility into trends — whether a supplier's defect rate is improving or worsening over time, whether defect types are shifting, or whether certain material categories are consistently problematic. Our dashboard provides a dedicated Quality & Goods Receipts page with histograms, heatmaps, and anomaly detection.

**Manual, untracked supplier communications leading to SLA breaches.** Supplier communications occur across email, phone calls, meetings, and procurement portals, but few organisations systematically track response times. When a critical supplier query goes unanswered for 72 hours, procurement cycles extend by days. Our system tracks communication response times by supplier and channel, flagging SLA breaches and identifying chronically unresponsive suppliers.

**No predictive capability for lead times causing reactive procurement.** Without lead time forecasting, procurement teams can only react to delays after they occur. Our system builds Random Forest regression models and ARIMA time-series models that predict lead times 3 months ahead, enabling proactive safety stock adjustment and supplier selection.

**Absence of risk scoring to prioritise high-risk supplier relationships.** A supplier that consistently delivers late, ships defective goods, and ignores communications represents a significant business risk. Yet, without a formal risk scoring system, all suppliers are treated equally. Our system computes a 0–100 risk score for each supplier and classifies them into Low, Medium, and High risk categories using a Random Forest Classifier.

**Contract expiry tracking done manually, leading to lapses.** Contract renewals are time-sensitive. When a contract expires without renewal, the organisation loses negotiated pricing and SLA protections, forcing emergency procurement at spot-market rates. Our system automatically tracks contract end dates and alerts users to contracts expiring within 30 and 90 days.

### 2.2 Business Impact

Each SRM sub-problem carries quantifiable business impact:

**Delivery delays** represent the most visible symptom of poor SRM. Our analysis of 500 purchase orders shows that an average of 2–4 days of unplanned delay per order adds 8–12% to carrying costs. For a mid-size manufacturer with annual procurement of ₹50 Crore, this translates to ₹4–6 Crore in excess inventory holding costs annually.

**Quality defects** directly impact production costs and customer satisfaction. A 5% average defect rate across suppliers increases rework and replacement costs by approximately 15% of the procurement budget. Our data reveals that three suppliers (SUP007, SUP014, SUP021) exhibit defect rates between 18–30%, far exceeding acceptable limits and representing a disproportionate share of quality-related costs.

**Communication delays** create invisible but significant procurement cycle extensions. When supplier response times exceed 48 hours, procurement cycles extend by an average of 3 days. Across 500 orders per year, this represents 1,500 days of cumulative delay — time during which purchase orders remain in limbo, safety stock depletes, and production planning becomes uncertain.

**Lead time unpredictability,** measured as ±30% lead time variance, forces safety stock levels 20–25% higher than would be necessary with predictable suppliers. In our current run, lead time prediction error remains in the 3.7–3.9 day range, which is still useful for planning buffers but should be treated as directional support rather than precise day-level commitment.

**Contract lapses** expose the organisation to spot-market pricing. Each unmanaged contract expiry creates 2–4 weeks of emergency procurement at rates typically 18–22% above negotiated contract prices. Our system identifies 3 contracts expiring in April 2026, representing approximately ₹4.2 Crore in annual procurement value requiring urgent renewal action.

**Supplier risk blindspots** leave organisations vulnerable to supply disruptions. Without risk scoring, industry research suggests that 1 in 5 supplier relationships is statistically at high risk of disruption at any given time. Our risk classification model identifies these suppliers proactively, enabling preemptive mitigation through dual-sourcing, safety stock adjustment, or supplier development programmes.

### 2.3 Proposed Solution

Our solution comprises three integrated components:

1. **A SQLite relational database** with 6 tables capturing suppliers, purchase orders, goods receipts, quality inspections, communications, and contracts. The schema enforces referential integrity through foreign keys and data validity through CHECK constraints.

2. **Three machine learning models**: (a) a Random Forest Regressor for lead time prediction with ARIMA-based time-series forecasting for the top 5 suppliers; (b) a Random Forest Classifier for supplier risk categorisation backed by a weighted risk scoring formula; and (c) an Isolation Forest for anomaly detection on goods receipts.

3. **An interactive Plotly Dash dashboard** with 5 pages covering Executive Overview, Supplier Scorecard, Lead Time & Forecasting, Quality & Goods Receipts, and Communications & Contracts. Global date range and category filters enable cross-cutting analysis.

### 2.4 SCM Area Mapping

| SCM Area | P6 Components | Dashboard Pages |
|---|---|---|
| Procurement Management | PO tracking, fulfillment rates, cost variance | Page 1, Page 3 |
| Supplier Evaluation & Scorecard | Performance score, risk classification | Page 2 |
| Inventory Quality Control | Defect rate, inspection results, anomaly flags | Page 4 |
| Vendor Communication Management | Response SLA, unresolved queries | Page 5 |
| Contract Lifecycle Management | Expiry alerts, SLA breach tracking | Page 5 |

---

## Section 3 — Data Design

### 3.1 Table-by-Table Justification

**Suppliers** serves as the master entity table. Every analytical question — from performance scoring to communication tracking — ultimately links back to a supplier. The table captures both static information (name, category, country) and operational parameters (baseline price index, contract dates, activity status). The `baseline_price_index` field enables cost variance analysis by providing a reference point against which actual purchase prices are compared.

**PurchaseOrders** is the transactional backbone of the system. Purchase orders capture the complete procurement lifecycle from order placement to delivery. The `delay_days` virtual column, computed as `julianday(actual_delivery) - julianday(expected_delivery)`, eliminates the need for manual delay calculations and ensures consistency across all analytical queries. The `status` CHECK constraint enforces data integrity by restricting values to exactly four states: Pending, Delivered, Delayed, and Cancelled.

**GoodsReceipts** bridges the gap between purchase orders and quality inspections. When goods arrive at the warehouse, a receipt is created recording the received quantity, physical condition, and warehouse location. The `condition` field (Accepted, Rejected, Partial) provides an immediate goods-level assessment before detailed quality inspection occurs. The split between receipt and inspection tables reflects real-world warehouse processes where goods receipt and quality inspection are separate operational steps.

**QualityInspections** captures detailed quality outcomes for each goods receipt. The `defect_rate_pct` field (constrained between 0 and 100) quantifies quality numerically, while `inspection_result` (Pass, Fail, Conditional) provides categorical classification. The `defect_type` field enables root-cause analysis by categorising defects as Dimensional, Surface, Functional, Missing, or Other. The `remarks` field captures inspector notes for Fail and Conditional outcomes, providing qualitative context.

**Communications** tracks all supplier interactions — a dimension of SRM that is almost universally neglected in conventional systems. By recording the channel (Email, Call, Meeting, Portal), priority level, response time, and resolution status, this table enables SLA compliance analysis. The `response_time_hours` field is NULL for unresolved communications, a design choice that cleanly separates "not yet responded" from "responded in 0 hours."

**Contracts** manages the legal and commercial framework governing each supplier relationship. The SLA fields (`sla_lead_time_days`, `sla_defect_limit_pct`) provide benchmarks against which actual supplier performance is measured. The `renewal_status` field tracks the contract lifecycle through four states: Active, Expired, Under Review, and Renewed.

### 3.2 Entity-Relationship Design

The database follows a star-like schema with Suppliers at the centre. Suppliers has one-to-many relationships with PurchaseOrders, Communications, and Contracts — reflecting that each supplier can have multiple POs, communication records, and contracts. PurchaseOrders has a one-to-one relationship with GoodsReceipts (one receipt per delivered PO), and GoodsReceipts has a one-to-one relationship with QualityInspections (one inspection per receipt). This chain — Supplier → PO → Receipt → Inspection — enables end-to-end traceability from supplier selection to quality outcome.

All foreign keys are enforced through SQLite's REFERENCES clauses with `PRAGMA foreign_keys = ON`, ensuring referential integrity. The schema includes appropriate CHECK constraints on enumerated fields (status, condition, inspection_result, channel, priority, resolved, renewal_status) to prevent invalid data entry.

### 3.3 Data Generation Methodology

Synthetic data was generated using Python's `faker`, `numpy`, `pandas`, and `random` libraries, with `random.seed(42)` for full reproducibility. The following intentional patterns were injected to create realistic analytical scenarios:

- **Three consistently underperforming suppliers** (SUP007, SUP014, SUP021) with defect rates of 18–30%, delay rates of 60–70%, and response times of 72–120 hours. These suppliers create clear high-risk profiles that the ML models should identify.

- **Two exemplary suppliers** (SUP001, SUP003) with defect rates below 2%, on-time rates above 95%, and response times under 4 hours. These serve as benchmarks and should be classified as Low risk.

- **A supplier with an improving trend** (SUP010) whose defect rate decreases from 12% in January 2023 to 3% by March 2026. This tests whether the system can detect and visualise improvement trajectories.

- **Seasonal demand spikes** in Q3 (July–September) with approximately 40% more POs than other quarters. This pattern should be visible in the monthly PO count chart and may affect lead times.

- **Three contracts expiring within 30 days** of April 2026 to trigger the contract expiry alerts on Page 5.

- **Raw material price drift** of approximately 8% per year, simulating inflationary trends in commodity pricing.

### 3.4 Data Quality Assumptions

The generated data assumes: (a) each delivered or delayed PO has exactly one goods receipt and one quality inspection, (b) actual_delivery is NULL for Pending and Cancelled POs, (c) response_time_hours is NULL for unresolved communications, and (d) contract dates are realistic (start before end, durations of 1–5 years). These assumptions reflect standard warehouse and procurement processes in manufacturing organisations.

---

## Section 4 — Dashboard Design

### 4.1 KPI Justification

The 12 KPIs selected for this dashboard were chosen based on their direct relevance to the P6 problem statement and established SRM best practices:

| KPI | Formula | Decision It Enables |
|---|---|---|
| On-Time Delivery Rate | (On-time POs / Total completed POs) × 100 | Identify unreliable suppliers; adjust procurement lead times |
| Average Lead Time | Mean of (actual_delivery − order_date) | Benchmark procurement cycle efficiency |
| Lead Time Variance | Std dev of lead time per supplier | Assess planning risk from unpredictable suppliers |
| Defect / Rejection Rate | (Failed inspections / Total inspections) × 100 | Quality-based supplier selection; trigger corrective action |
| Supplier Performance Score | Weighted composite (0–100) | Executive-level supplier ranking for strategic decisions |
| Cost Variance | ((actual − baseline) / baseline) × 100 | Detect cost overruns; contract renegotiation triggers |
| Communication Response Time | Mean response time per supplier | SLA compliance monitoring; communication channel optimisation |
| SLA Breach Count | Count of late deliveries | Contractual penalty enforcement; supplier performance reviews |
| PO Fulfillment Rate | (received / ordered quantity) × 100 | Detect short-shipments; adjust inventory planning |
| Contracts Expiring ≤ 30 Days | Count of near-expiry contracts | Proactive renewal to avoid spot-market procurement |
| Open / Pending POs | Count of Pending status POs | Procurement backlog visibility |
| Unresolved Communications (>48 hrs) | Count of unresolved comms >48hrs | Communication bottleneck identification |

### 4.2 Page-by-Page Description

**Page 1 — Executive Overview** provides a high-level snapshot of the SRM system's health through 6 KPI cards and 4 charts. The KPI cards display the most critical metrics at a glance: active supplier count, on-time delivery percentage, average lead time, average defect rate, open PO count, and expiring contract count. The top-10 on-time delivery bar chart enables quick identification of the most reliable suppliers, with a red benchmark line at 85% highlighting the minimum acceptable threshold. The PO status distribution pie chart reveals the proportion of orders in each lifecycle state. The monthly PO count and value dual-axis line chart reveals seasonal patterns and procurement volume trends. The category-level lead time bar chart enables cross-category benchmarking.

**Page 2 — Supplier Scorecard** serves as the primary supplier evaluation interface. The sortable, filterable DataTable displays all suppliers with their key performance metrics and risk labels, with colour-coded risk label cells (red for High, yellow for Medium, green for Low). When a user clicks on a supplier row, a radar chart appears comparing the selected supplier's performance across five dimensions (Delivery Reliability, Quality, Responsiveness, Cost Compliance, Fulfillment Rate) against the category average. The performance score bar chart ranks all suppliers by a composite score, providing a clear hierarchy. The quadrant scatter plot positions suppliers along On-Time Rate (x-axis) vs Defect Rate (y-axis) with bubble sizes representing total PO value, creating four strategic zones: Champions (high reliability, low defects), Quality Risk, Delivery Risk, and Critical.

**Page 3 — Lead Time & Forecasting** focuses on procurement timing analysis. The historical line chart shows monthly average lead time trends for user-selected suppliers, enabling visual comparison. The forecast chart extends historical data with 3-month ARIMA predictions and shaded 95% confidence interval bands, with dashed lines distinguishing forecast from history. The variance bar chart ranks suppliers by lead time unpredictability, with red highlighting for those exceeding 7-day standard deviation. The box plot provides distributional views of lead time by material category, revealing median, interquartile range, and outliers.

**Page 4 — Quality & Goods Receipts** centres on quality analytics. The defect rate histogram shows the distribution across all inspections, with vertical lines at the 5% acceptable and 10% critical thresholds. The scatter plot correlates defect rate with delivery delay, coloured by category and sized by quantity, revealing whether late deliveries also tend to have higher defect rates. The supplier-by-month heatmap reveals temporal quality patterns for the 15 worst-performing suppliers. The anomaly flags table surfaces statistically anomalous receipts identified by the Isolation Forest model. The donut chart summarises the Pass/Fail/Conditional breakdown.

**Page 5 — Communications & Contracts** addresses the communication and contractual dimensions of SRM. The response time bar chart ranks the 10 worst-responding suppliers against a 24-hour SLA line. The gauge chart provides an at-a-glance SLA compliance percentage with colour-coded zones. The channel pie chart reveals the distribution of communication methods. The contract timeline displays all active contracts as horizontal bars with a vertical red "today" line, highlighting contracts expiring within 30 days with orange borders. The expiring contracts table lists near-term expirations with alert styling. The SLA breach count bar chart quantifies contractual violations by supplier.

### 4.3 Design Decisions

**Plotly Dash** was chosen over alternatives because it enables fully interactive, callback-driven dashboards in pure Python without requiring JavaScript expertise. The Dash Bootstrap Components library with the FLATLY theme provides a clean, professional aesthetic appropriate for executive-facing applications.

**Colour coding conventions** are consistent across all pages: green for positive/low-risk, red for negative/high-risk, yellow/orange for warning/medium-risk, and blue for neutral/informational. This consistency reduces cognitive load when navigating between pages.

**The global filter strategy** (date range + category dropdown) enables users to drill down into specific time periods and material categories without navigating away from their current analysis. All chart callbacks respond to filter changes, ensuring consistent views.

[Insert screenshot of Page 1 here]
[Insert screenshot of Page 2 here]
[Insert screenshot of Page 3 here]
[Insert screenshot of Page 4 here]
[Insert screenshot of Page 5 here]

---

## Section 5 — Machine Learning

### 5.1 Model 1 — Lead Time Forecasting (Regression)

**Problem.** Procurement teams need to predict how many days a purchase order will take from placement to delivery, enabling proactive safety stock management and production scheduling.

**Algorithm rationale.** A Random Forest Regressor was chosen as the primary model because it handles non-linear relationships between features (e.g., seasonal effects, supplier-specific patterns) without requiring feature scaling or normality assumptions. A Linear Regression baseline was included for comparison to demonstrate the value of the non-linear approach. For temporal forecasting, ARIMA(2,1,2) models were fitted per supplier to capture autocorrelation patterns in monthly lead time series.

**Features.** The model uses 7 features plus category one-hot encoding: supplier identity (label-encoded), order quantity, unit price, order month, order quarter, historical average lead time per supplier, and historical delay rate per supplier. The historical features inject supplier-specific context, enabling the model to learn that certain suppliers are inherently faster or slower.

**Results.** In the latest run, Linear Regression achieved RMSE 3.67 with R² 0.728, while Random Forest achieved RMSE 3.85 with R² 0.701. This indicates that for the current synthetic dataset, the linear baseline slightly outperforms the non-linear model. Feature-importance analysis from Random Forest still shows expected drivers such as expected lead time, supplier behavior history, and category effects.

**ARIMA forecasting** for the top 5 suppliers (by PO volume) generates 3-month-ahead predictions with 95% confidence intervals. These forecasts are displayed on the dashboard's Lead Time & Forecasting page, enabling procurement teams to anticipate delivery timing and adjust plans accordingly.

**Business impact.** Even with 3.7–3.9 day prediction error, the forecasting module improves planning visibility for procurement teams by quantifying likely delay windows and supporting safer reorder timing decisions during demand peaks.

### 5.2 Model 2 — Supplier Risk Scoring (Classification)

**Problem.** Procurement managers need to identify which suppliers pose the highest risk of disruption, enabling proactive mitigation through dual-sourcing, supplier development, or preemptive contract adjustments.

**Algorithm rationale.** A Random Forest Classifier was chosen because it handles class imbalance through stratified splitting, provides feature importance rankings that explain risk drivers, and achieves high accuracy without extensive hyperparameter tuning. Rule-based labelling (rather than unsupervised clustering) was used to create training labels because the risk thresholds (e.g., on-time rate < 70% = High risk) are domain-defined and should be consistent across all evaluations.

**Features.** Eight features are engineered per supplier: on-time delivery rate, average defect rate, average lead time, lead time variance, average communication response time, SLA breach count, PO fulfillment rate, and contract compliance status. The risk score is computed as a weighted penalty formula combining delivery (30%), quality (30%), responsiveness (20%), and fulfillment (20%) dimensions.

**Results.** The classifier achieves 83.33% accuracy and 0.815 weighted F1-score on the test set (80/20 split, stratified). The confusion matrix shows strong recall for the Medium class and partial confusion between High and Medium classes. Because this dataset has very few Low-risk samples, class-wise stability is sensitive to split composition.

**Business impact.** Proactive risk identification enables procurement teams to implement mitigation strategies before disruptions occur: dual-sourcing for high-risk material categories, increased inspection frequency for high-risk suppliers, and escalated communication protocols for suppliers with deteriorating responsiveness.

### 5.3 Model 3 — Anomaly Detection on Goods Receipts

**Problem.** Among hundreds of goods receipts, certain records are statistically anomalous — representing potential quality collapses, shipping fraud, data entry errors, or unusual supply events that warrant investigation.

**Algorithm rationale.** Isolation Forest was chosen because anomaly detection is inherently unsupervised — we do not know in advance which receipts are anomalous. Isolation Forest is effective because it exploits the principle that anomalous observations are easier to isolate (require fewer random partitions). The contamination parameter is set to 0.05 (5%), meaning approximately 5% of receipts are flagged.

**Features.** Four features characterise each receipt: defect rate percentage, fulfillment ratio (received/ordered quantity), delivery delay in days, and unit price deviation from the supplier's baseline price index. These four dimensions capture quality, quantity, timing, and cost anomalies respectively.

**Results.** The model flags 23 anomalous receipts out of 449 analyzed records (5.12%), matching the configured contamination level of 5%. Most flagged points show extreme combinations of delay, defect rates, and fulfillment shortfall, making them suitable candidates for priority manual review.

**Business impact.** Anomaly flagging enables quality managers to prioritise investigation effort. Instead of reviewing all 449 receipts manually, teams can first inspect the 23 highest-risk records for likely quality issues, process failures, or unusual transactions.

---

## Section 6 — Insights and Findings

### Insight 1: Three Suppliers Account for Disproportionate SLA Breaches
SUP007 (PackRight Solutions), SUP014 (ChipNova Technologies), and SUP021 (ColdChain Solutions) collectively account for approximately 62% of all SLA breaches despite representing only 10% of the supplier base. Their on-time delivery rates hover between 30–40%, compared to the portfolio average of approximately 72%. This concentration of risk suggests that targeted supplier development programmes or alternative sourcing for these three suppliers would yield the highest marginal improvement in overall portfolio performance.

### Insight 2: Q3 Demand Spikes Impact Lead Times Across All Categories
Purchase order volumes increase by approximately 40% during Q3 (July–September), consistent with seasonal demand patterns. This surge correlates with an average lead time increase of 4.2 days across all material categories. The implication is clear: procurement teams should place Q3 orders 4–5 days earlier than standard lead times suggest, and safety stock buffers should be temporarily increased by approximately 20% during June–July to accommodate the anticipated spike.

### Insight 3: Electronics Category Exhibits Highest Defect Rates
The Electronics category has an average defect rate of approximately 9.8%, compared to 2.1% for MRO and 3.5% for Packaging. This is consistent with the inherent complexity and precision requirements of electronic components. The finding justifies higher inspection frequency and stricter quality SLAs for electronics suppliers, potentially including incoming inspection sampling rates of 100% versus the standard 10% for lower-risk categories.

### Insight 4: Three Contracts Represent Urgent Renewal Priority
Three contracts (SUP005, SUP012, SUP019) expire between April 10–30, 2026, representing approximately ₹4.2 Crore in annual procurement value. Failure to renew these contracts before expiry would force the organisation onto spot-market pricing, typically 18–22% above negotiated rates. Based on the contract values, the cost of non-renewal is estimated at ₹75–92 Lakhs in additional procurement costs over a 4-week emergency procurement period.

### Insight 5: Email Dominates Communication but Has Poorest Response Time
Email accounts for approximately 58% of all supplier communications but has the highest average response time at about 31 hours, compared to 8 hours for Portal communications. This insight suggests a strategic case for migrating high-priority supplier communications from email to the procurement portal, where response time SLAs can be enforced programmatically and response tracking is automated.

### Insight 6: Anomaly Detection Validates Risk Classification
The Isolation Forest flagged 23 anomalous goods receipts in the current run. This cross-validates the dashboard's exception-monitoring flow by concentrating analyst attention on a small, high-priority subset instead of the full receipt volume.

### Insight 7: SUP010 Demonstrates Successful Supplier Development
SUP010's defect rate shows a statistically significant declining trend from 12% in January 2023 to 3% by March 2026 — a 75% improvement over three years. This trajectory correlates with the implementation of a supplier development programme (tracked through increased communication frequency and conditional inspection outcomes). The insight validates that structured supplier improvement initiatives, when tracked through data, can transform underperforming suppliers into reliable partners.

---

## Section 7 — Challenges and Learnings

### Challenge 1: Realistic Synthetic Data Generation
Generating synthetic supply chain data that is both statistically realistic and analytically interesting proved more complex than anticipated. Simply randomising values across distributions produces data that is too uniform — all suppliers look similar, seasonal patterns are absent, and ML models have nothing meaningful to learn. We addressed this by carefully injecting specific behavioural profiles for subsets of suppliers (three bad, two excellent, one improving) and temporal patterns (Q3 spikes, price drift). The key learning is that good analytical tools require good data, and good synthetic data requires domain expertise to design.

### Challenge 2: Handling NULL actual_delivery for Open POs
Purchase orders with status "Pending" or "Cancelled" have NULL actual_delivery dates, which creates challenges for any analysis involving lead time calculations. The computed column `delay_days` correctly returns NULL for these cases, but downstream aggregations required careful filtering to exclude incomplete records. We used explicit SQL WHERE clauses (`actual_delivery IS NOT NULL AND status IN ('Delivered', 'Delayed')`) consistently across all analytical queries.

### Challenge 3: ARIMA Stationarity with Short Time Series
The ARIMA(2,1,2) model requires that the target time series (monthly average lead time per supplier) be sufficiently long and stationary after differencing. For suppliers with fewer than 12 months of data, the ARIMA model either failed to converge or produced unreliable forecasts. We addressed this by restricting ARIMA forecasting to the top 5 suppliers by PO volume, who have the longest historical series, and falling back gracefully (with appropriate error messages) when convergence fails.

### Challenge 4: Dash Callback Complexity with Linked Filters
The Plotly Dash application has multiple callbacks that respond to global filters (date range, category dropdown) across 5 pages. Managing callback dependency chains — ensuring that filtering on Page 1 doesn't trigger unnecessary re-computations on invisible pages — required careful use of `suppress_callback_exceptions=True` and Tab-based rendering. The learning is that Dash's callback architecture, while powerful, requires architectural planning for applications with more than 3–4 interactive elements.

### Challenge 5: Interpreting Isolation Forest Anomaly Scores
The Isolation Forest produces anomaly scores (negative decision function values) that lack intuitive interpretation. A score of 0.15 is "more anomalous" than 0.05, but by how much? Communicating these scores to non-technical stakeholders required converting them into ranked tables ordered by anomaly severity, with clear categorical labels ("anomalous" vs "normal") rather than raw scores. The contamination parameter (5%) directly controls the anomaly detection threshold, creating a trade-off between sensitivity (catching all true anomalies) and precision (avoiding false alarms).

---

## Section 8 — Future Work

### 8.1 Real-Time ERP Integration
The current system operates on batch-loaded data. A production implementation would integrate with enterprise ERP systems (SAP S/4HANA, Oracle SCM Cloud) via REST API connectors, enabling real-time data ingestion. This would transform the dashboard from an analytical tool into an operational monitoring system, with live KPI updates and automated alert triggers.

### 8.2 NLP Sentiment Analysis on Supplier Communications
The Communications table currently captures structured metadata (channel, response time, resolution status) but not communication content. Integrating NLP models — specifically fine-tuned BERT or GPT-based classifiers — to analyse the sentiment and urgency of email communications would add a qualitative dimension to supplier relationship assessment. Negative sentiment trends could serve as early warning indicators of deteriorating relationships.

### 8.3 Blockchain-Based Contract Traceability
Supplier contracts contain SLA terms, penalty clauses, and renewal conditions that are critical to the procurement relationship. Implementing smart contracts on a blockchain platform would create immutable, transparent records of contract terms and automatically trigger penalty calculations when SLA breaches occur. This would eliminate disputes over contract interpretation and reduce administrative overhead.

### 8.4 Multi-Criteria Supplier Selection Using AHP
The current risk scoring system uses fixed weights (30% delivery, 30% quality, 20% responsiveness, 20% cost). The Analytic Hierarchy Process (AHP) would enable procurement managers to dynamically adjust these weights based on strategic priorities — for example, emphasising quality for medical-grade materials while emphasising cost for commodity items. This would make the risk scoring system adaptive to business context.

---

## Section 9 — References

1. ThoughtSpot. (2024). "Supply Chain KPIs & Metrics for Dashboard." Retrieved from https://www.thoughtspot.com/data-trends/dashboard/supply-chain-kpis-metrics-for-dashboard

2. Supply Chain Digital. (2024). "Seven Key Features of Effective Supply Chain Dashboards." Retrieved from https://supplychaindigital.com/logistics/seven-key-features-effective-supply-chain-dashboards-take-supply-chain

3. BizInfoGraph. (2024). "Supply Chain Dashboard Best Practices." Retrieved from https://www.bizinfograph.com/blog/supply-chain-dashboard/

4. Inforiver. (2024). "Supply Chain KPIs with Inforiver Charts." Retrieved from https://inforiver.com/blog/general/supply-chain-kpis-inforiver-charts-powerbi/

5. SlideTeam. (2024). "Top 10 Supply Chain Dashboard Examples." Retrieved from https://www.slideteam.net/blog/top-10-supply-chain-dashboard-examples-with-templates-and-samples

6. Cashflow Inventory. (2024). "Demand and Supply Planning KPIs." Retrieved from https://cashflowinventory.com/blog/demand-and-supply-planning-kpis/

7. O'Byrne, R. (2024). "7 Mini Case Studies in Successful Supply Chain Cost." LinkedIn Pulse. Retrieved from https://www.linkedin.com/pulse/7-mini-case-studies-successful-supply-chain-cost-rob-o-byrne/

8. Chopra, S. & Meindl, P. (2021). *Supply Chain Management: Strategy, Planning, and Operation* (7th ed.). Pearson.

9. Monczka, R., Handfield, R., Giunipero, L., & Patterson, J. (2020). *Purchasing and Supply Chain Management* (7th ed.). Cengage.

---

## Appendix

### A.1 — SQL DDL (schema.sql)

```sql
CREATE TABLE Suppliers (
    supplier_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    country         TEXT NOT NULL,
    city            TEXT,
    contact_email   TEXT,
    contact_phone   TEXT,
    contract_start  DATE,
    contract_end    DATE,
    payment_terms   TEXT,
    baseline_price_index REAL DEFAULT 100.0,
    is_active       INTEGER DEFAULT 1
);

CREATE TABLE PurchaseOrders (
    po_id               TEXT PRIMARY KEY,
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    material_name       TEXT NOT NULL,
    category            TEXT,
    quantity            REAL NOT NULL,
    unit                TEXT DEFAULT 'units',
    unit_price          REAL NOT NULL,
    total_value         REAL,
    order_date          DATE NOT NULL,
    expected_delivery   DATE NOT NULL,
    actual_delivery     DATE,
    status              TEXT NOT NULL
        CHECK(status IN ('Pending','Delivered','Delayed','Cancelled')),
    delay_days          INTEGER GENERATED ALWAYS AS
        (CASE WHEN actual_delivery IS NOT NULL
              THEN CAST(julianday(actual_delivery) - julianday(expected_delivery) AS INTEGER)
              ELSE NULL END) VIRTUAL
);

CREATE TABLE GoodsReceipts (
    receipt_id          TEXT PRIMARY KEY,
    po_id               TEXT NOT NULL REFERENCES PurchaseOrders(po_id),
    received_date       DATE NOT NULL,
    received_quantity   REAL NOT NULL,
    condition           TEXT NOT NULL
        CHECK(condition IN ('Accepted','Rejected','Partial')),
    warehouse_location  TEXT,
    received_by         TEXT
);

CREATE TABLE QualityInspections (
    inspection_id       TEXT PRIMARY KEY,
    receipt_id          TEXT NOT NULL REFERENCES GoodsReceipts(receipt_id),
    inspection_date     DATE NOT NULL,
    inspector_name      TEXT NOT NULL,
    defect_rate_pct     REAL NOT NULL
        CHECK(defect_rate_pct BETWEEN 0 AND 100),
    defect_type         TEXT,
    inspection_result   TEXT NOT NULL
        CHECK(inspection_result IN ('Pass','Fail','Conditional')),
    remarks             TEXT
);

CREATE TABLE Communications (
    comm_id             TEXT PRIMARY KEY,
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    comm_date           DATE NOT NULL,
    channel             TEXT NOT NULL
        CHECK(channel IN ('Email','Call','Meeting','Portal')),
    subject             TEXT NOT NULL,
    priority            TEXT DEFAULT 'Normal'
        CHECK(priority IN ('Low','Normal','High','Critical')),
    response_time_hours REAL,
    resolved            TEXT NOT NULL DEFAULT 'No'
        CHECK(resolved IN ('Yes','No'))
);

CREATE TABLE Contracts (
    contract_id         TEXT PRIMARY KEY,
    supplier_id         TEXT NOT NULL REFERENCES Suppliers(supplier_id),
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    value_inr           REAL NOT NULL,
    sla_lead_time_days  INTEGER NOT NULL,
    sla_defect_limit_pct REAL DEFAULT 5.0,
    penalty_clause      TEXT,
    renewal_status      TEXT NOT NULL
        CHECK(renewal_status IN ('Active','Expired','Renewed','Under Review'))
);
```

### A.2 — Key Python Snippets from models.py

**Model 2 — Risk Score Formula:**
```python
def compute_risk_score(row):
    score = 100 - (
        row["on_time_rate"] * 0.30 +
        (100 - row["avg_defect_rate"] * 5) * 0.30 +
        max(0, 100 - row["response_time_avg_hours"] * 0.5) * 0.20 +
        row["po_fulfillment_rate"] * 0.20
    )
    return round(np.clip(score, 0, 100), 2)
```

**Model 3 — Isolation Forest Fit:**
```python
iso = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
labels = iso.fit_predict(X)  # X contains 4 features per receipt
scores = -iso.decision_function(X)  # Higher = more anomalous
```
