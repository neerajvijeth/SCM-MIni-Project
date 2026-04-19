# Supplier Relationship Management (SCM P6)

A small **end-to-end supply-chain analytics demo** for coursework **Problem Statement P6**. It turns synthetic supplier and order data into **KPIs, charts, and ML insights** so you can explore how procurement teams might monitor delivery, quality, risk, and contracts in one place.

---

## What this project does

- **Stores** supplier, purchase order, goods receipt, quality, communication, and contract data in **SQLite** (`scm_p6.db`), with CSV exports you can inspect directly.
- **Trains three ML helpers**: lead-time style forecasting, supplier **risk bands**, and **anomaly** flags on goods receipts. Outputs are saved as CSV/JSON and picked up by the apps.
- **Shows everything in a browser**:
  - **Main experience:** a **Plotly Dash** dashboard with five tabs (executive view, scorecards, lead time, quality/receipts, communications & contracts).
  - **Optional:** a **FastAPI** backend plus a **React (Vite)** frontend that reads the same generated files for a lighter API-driven UI.

---

## Tech stack

| Area | Tools |
|------|--------|
| Data | Python, SQLite, pandas |
| ML | scikit-learn, statsmodels (and related libs in `requirements.txt`) |
| Main UI | Plotly Dash, Dash Bootstrap Components |
| Optional API/UI | FastAPI, Uvicorn, React, Vite |

---

## Prerequisites

- **Python 3.10+** (`python --version` or `python3 --version`)
- For the optional React app: **Node.js** (includes `npm`)

---

## Quick start (main Dash dashboard)

Run these from the **project root** (the folder that contains `app.py`).

1. **Create and activate a virtual environment** (recommended)

   ```bash
   python -m venv venv
   ```

   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the database and sample CSV data**

   ```bash
   python generate_data.py
   ```

4. **Train models and write ML outputs** (CSV/JSON used by the dashboard)

   ```bash
   python models.py
   ```

5. **Start the dashboard**

   ```bash
   python app.py
   ```

6. **Open in your browser:** [http://127.0.0.1:8050/](http://127.0.0.1:8050/)  
   Stop the server with `Ctrl+C` in the terminal.

> **Note:** If `python` is not found, try `py` (Windows) or `python3` (macOS/Linux).

---

## Optional: React UI + FastAPI

Use this if you want a separate REST API and a minimal React front end. **Complete steps 1–4 above first** so CSVs and `model_metrics.json` exist.

**Terminal 1 — API**

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend**

```bash
cd frontend
npm install
npm run dev
```

- **API:** [http://127.0.0.1:8000](http://127.0.0.1:8000) (e.g. [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive docs)
- **React app:** [http://127.0.0.1:5173](http://127.0.0.1:5173)

**Example endpoints:** `GET /api/health`, `GET /api/summary`, `GET /api/risk-suppliers`, `GET /api/anomalies`, `GET /api/leadtime-forecast`, `GET /api/model-metrics`

---

## Project layout (important files)

| File / folder | Role |
|---------------|------|
| `generate_data.py` | Builds `scm_p6.db` and CSVs from synthetic scenarios |
| `schema.sql` | SQL schema reference |
| `models.py` | Trains models; writes predictions, risk scores, anomalies, metrics |
| `app.py` | Dash dashboard (main UI) |
| `scm_p6.db` | SQLite database (created by `generate_data.py`) |
| `*.csv`, `model_metrics.json` | Data + ML outputs used by `app.py` and `backend/` |
| `backend/main.py` | FastAPI app (optional) |
| `frontend/` | React + Vite app (optional) |
| `assets/dashboard.css` | Dash styling |
| `report.md`, `presentation_outline.md` | Course/report materials |
| `END_TO_END_PROJECT_EXPLANATION.md` | Longer architecture and business walkthrough |

---

## Troubleshooting

- **Empty charts or errors in Dash:** Run `generate_data.py` then `models.py` again so the database and ML files match.
- **API or React errors:** Confirm CSVs and `model_metrics.json` exist in the project root after running `models.py`.

---

## Academic context

Built for **SCME P6 — Supplier Relationship Management (SRM)**. For deeper detail on architecture, models, and dashboard pages, see `END_TO_END_PROJECT_EXPLANATION.md` and `report.md`.
