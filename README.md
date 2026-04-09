# SCME P6: Supplier Relationship Management

This project is a complete, full-stack Supplier Relationship Management (SRM) platform built with Python, Plotly Dash, Scikit-Learn, and SQLite. It addresses **Problem Statement P6** for the SCME course by providing an interactive 5-page dashboard that integrates 3 Machine Learning models.

## Features
- **Database:** Synthetic SQLite database with 6 tables mapping purchase orders, suppliers, contracts, quality inspections, and communications.
- **ML Integration:**
  - Lead Time Forecasting (Random Forest + ARIMA)
  - Supplier Risk Classification (Random Forest Classifier)
  - Anomaly Detection in Goods Receipts (Isolation Forest)
- **Interactive Dashboard:** 5 unique pages with global filters to monitor executive KPIs, supplier performance scorecards, lead times, quality defects, and communication SLAs.

---

## 🚀 How to Run the Project from Scratch

Follow these steps to set up and run the dashboard on your local machine.

### Prerequisites
Make sure you have **Python 3.10+** installed. You can check your version by running:
```bash
python3 --version
```

### 1. Create a Virtual Environment
It is highly recommended to run this project inside an isolated virtual environment so it doesn't interfere with your system's Python packages.

Open your terminal, navigate to the project folder, and run:
```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment
Activate the environment you just created.
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```
*(You will know it's activated if you see `(venv)` at the beginning of your terminal prompt).*

### 3. Install Dependencies
With the environment activated, install all the required Python libraries:
```bash
pip install -r requirements.txt
```

### 4. Generate the Database & Sample Data
Run the data generator. This creates the `scm_p6.db` SQLite database and populated CSV files with 30 simulated suppliers and historical purchase orders.
```bash
python generate_data.py
```

### 5. Train the Machine Learning Models
Run the ML script to train the models and generate prediction CSVs (`lead_time_predictions.csv`, `supplier_risk_scores.csv`, `anomaly_flags.csv`). This process takes ~10-15 seconds.
```bash
python models.py
```

### 6. Start the Dashboard
Finally, launch the Plotly Dash web application:
```bash
python app.py
```

### 7. View the Dashboard
Once the server starts, it will say `Dash is running on http://127.0.0.1:8050/`.
Open your web browser (Chrome, Firefox, Safari) and go to: **[http://127.0.0.1:8050/](http://127.0.0.1:8050/)**

To stop the server at any time, go to your terminal and press `Control + C`.

---

## 🗂 Project Structure
* `app.py`: The main Plotly Dash web server and frontend code.
* `models.py`: Scikit-learn machine learning pipelines.
* `generate_data.py`: Script to construct the database schema and populate it with synthetic records.
* `schema.sql`: Raw SQL definition of the database.
* `report.md` & `presentation_outline.md`: Academic deliverables and documentation.
* `requirements.txt`: Python package dependencies.

---

## React + FastAPI (Simple UI)

This repository now also includes a minimal full-stack version:
- `backend/main.py` (FastAPI)
- `frontend/` (React + Vite)

### 1) Start Backend
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 2) Start Frontend
```bash
cd frontend
npm install
npm run dev
```

Open: `http://127.0.0.1:5173`

### Available API Endpoints
- `GET /api/health`
- `GET /api/summary`
- `GET /api/risk-suppliers?limit=10`
- `GET /api/anomalies?limit=15`
- `GET /api/leadtime-forecast`
- `GET /api/model-metrics`
