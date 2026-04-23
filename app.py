"""
SCME P6 — Supplier Relationship Management
Interactive Dashboard (Plotly Dash + Dash Bootstrap Components)
5 Tabbed Pages: Executive Overview, Supplier Scorecard, Lead Time & Forecasting,
                Quality & Goods Receipts, Communications & Contracts

Run: python app.py  (after generate_data.py and models.py)
Dashboard: http://localhost:8050
"""

import os
import sqlite3
from datetime import datetime, timedelta

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ============================================================
# Configuration
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scm_p6.db")

# Reference date for "today" in this project
TODAY = datetime(2026, 4, 9)

# Material categories
CATEGORIES = ["Raw Materials", "Packaging", "Electronics", "Logistics", "MRO"]

# ============================================================
# Database Helper
# ============================================================
def query_db(sql, params=()):
    """Execute a SQL query and return a DataFrame. Opens and closes connection safely."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
    return df


# ============================================================
# Load Data
# ============================================================
def load_all_data():
    """Load all data from DB and CSVs at startup."""
    data = {}

    # From database
    data["suppliers"] = query_db("SELECT * FROM Suppliers")
    data["purchase_orders"] = query_db("SELECT * FROM PurchaseOrders")
    data["goods_receipts"] = query_db("SELECT * FROM GoodsReceipts")
    data["inspections"] = query_db("SELECT * FROM QualityInspections")
    data["communications"] = query_db("SELECT * FROM Communications")
    data["contracts"] = query_db("SELECT * FROM Contracts")

    # From ML output CSVs
    risk_path = os.path.join(BASE_DIR, "supplier_risk_scores.csv")
    pred_path = os.path.join(BASE_DIR, "lead_time_predictions.csv")
    anomaly_path = os.path.join(BASE_DIR, "anomaly_flags.csv")

    data["risk_scores"] = pd.read_csv(risk_path) if os.path.exists(risk_path) else pd.DataFrame()
    data["predictions"] = pd.read_csv(pred_path) if os.path.exists(pred_path) else pd.DataFrame()
    data["anomalies"] = pd.read_csv(anomaly_path) if os.path.exists(anomaly_path) else pd.DataFrame()

    # Parse dates
    for col in ["order_date", "expected_delivery", "actual_delivery"]:
        data["purchase_orders"][col] = pd.to_datetime(data["purchase_orders"][col], errors="coerce")
    data["communications"]["comm_date"] = pd.to_datetime(data["communications"]["comm_date"], errors="coerce")
    data["contracts"]["start_date"] = pd.to_datetime(data["contracts"]["start_date"], errors="coerce")
    data["contracts"]["end_date"] = pd.to_datetime(data["contracts"]["end_date"], errors="coerce")
    data["inspections"]["inspection_date"] = pd.to_datetime(data["inspections"]["inspection_date"], errors="coerce")

    # Parse predictions month column if present
    if not data["predictions"].empty and "month" in data["predictions"].columns:
        data["predictions"]["month"] = pd.to_datetime(data["predictions"]["month"], errors="coerce")

    return data


DATA = load_all_data()

# ============================================================
# Dash App
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "SRM Dashboard — SCME P6"

# ============================================================
# Color Palette
# ============================================================
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#18BC9C",
    "accent": "#3498DB",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "success": "#27AE60",
    "light": "#ECF0F1",
    "dark": "#2C3E50",
    "card_bg": "#FFFFFF",
    "risk_high": "#E74C3C",
    "risk_medium": "#F39C12",
    "risk_low": "#27AE60",
}

GRAPH_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
    "responsive": True,
}


def make_graph(graph_id: str):
    return dcc.Graph(id=graph_id, config=GRAPH_CONFIG, className="chart-graph")


def graph_col(graph_id: str, md: int):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(make_graph(graph_id), className="p-2"),
            className="graph-card h-100",
        ),
        md=md,
        className="mb-3",
    )


# ============================================================
# KPI Card Component
# ============================================================
def make_kpi_card(title, value, icon="📊", color=COLORS["accent"]):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "28px", "marginRight": "10px"}),
                html.Span(title, style={
                    "fontSize": "13px", "color": "#7f8c8d", "fontWeight": "500",
                    "textTransform": "uppercase", "letterSpacing": "0.5px",
                }),
            ], style={"marginBottom": "8px"}),
            html.H3(value, style={
                "color": color, "fontWeight": "700", "margin": "0",
                "fontSize": "28px",
            }),
        ]),
        style={
            "borderLeft": f"4px solid {color}",
            "borderRadius": "8px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
        },
        className="mb-3",
    )


# ============================================================
# Global Filters
# ============================================================
global_filters = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Date Range", className="fw-bold mb-1",
                           style={"fontSize": "13px", "color": "#7f8c8d"}),
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed="2023-01-01",
                    max_date_allowed="2026-04-20",
                    start_date="2023-01-01",
                    end_date="2026-03-31",
                    display_format="DD MMM YYYY",
                    style={"width": "100%"},
                ),
            ], md=6),
            dbc.Col([
                html.Label("Category", className="fw-bold mb-1",
                           style={"fontSize": "13px", "color": "#7f8c8d"}),
                dcc.Dropdown(
                    id="category-filter",
                    options=[{"label": "All Categories", "value": "All"}] +
                            [{"label": c, "value": c} for c in
                             ["Raw Materials", "Packaging", "Electronics", "Logistics", "MRO"]],
                    value="All",
                    clearable=False,
                    style={"fontSize": "14px"},
                ),
            ], md=4),
            dbc.Col([
                html.Div(style={"height": "22px"}),
                dbc.Button("Reset Filters", id="reset-btn", color="secondary",
                           outline=True, size="sm", className="w-100"),
            ], md=2),
        ]),
    ]),
    className="mb-3",
    style={"borderRadius": "8px", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"},
)


# ============================================================
# Page 1 — Executive Overview
# ============================================================
def page_executive():
    return html.Div([
        # KPI Cards Row
        html.Div(id="exec-kpi-cards"),
        dbc.Row([graph_col("exec-ontime-bar", 6), graph_col("exec-status-pie", 6)], className="g-2"),
        dbc.Row([graph_col("exec-monthly-line", 7), graph_col("exec-category-bar", 5)], className="g-2"),
    ], className="tab-page")


# ============================================================
# Page 2 — Supplier Scorecard
# ============================================================
def page_scorecard():
    risk_df = DATA["risk_scores"]

    # Prepare table data
    if not risk_df.empty:
        # Merge with supplier details
        supp = DATA["suppliers"][["supplier_id", "country"]].copy()
        table_df = risk_df.merge(supp, on="supplier_id", how="left")
        if "risk_label" not in table_df.columns:
            table_df["risk_label"] = table_df.get("predicted_label", "Unknown")

        # Compute avg lead time per supplier
        po_completed = DATA["purchase_orders"][
            DATA["purchase_orders"]["actual_delivery"].notna()
        ].copy()
        po_completed["lead_time"] = (
            po_completed["actual_delivery"] - po_completed["order_date"]
        ).dt.days
        avg_lt = po_completed.groupby("supplier_id")["lead_time"].mean().round(1).reset_index()
        avg_lt.columns = ["supplier_id", "avg_lead_time"]
        table_df = table_df.merge(avg_lt, on="supplier_id", how="left")
        table_df["avg_lead_time"] = table_df["avg_lead_time"].fillna(0)

        table_data = table_df.to_dict("records")
        table_columns = [
            {"name": "Supplier ID", "id": "supplier_id"},
            {"name": "Supplier", "id": "name"},
            {"name": "Category", "id": "category"},
            {"name": "Country", "id": "country"},
            {"name": "On-Time %", "id": "on_time_rate", "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Defect Rate %", "id": "avg_defect_rate", "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Avg Lead Time", "id": "avg_lead_time", "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Risk Score", "id": "risk_score", "type": "numeric",
             "format": {"specifier": ".1f"}},
            {"name": "Risk Label", "id": "risk_label"},
        ]
    else:
        table_data = []
        table_columns = []

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        dash_table.DataTable(
                            id="scorecard-table",
                            columns=table_columns,
                            data=table_data,
                            hidden_columns=["supplier_id"],
                            sort_action="native",
                            filter_action="native",
                            page_size=10,
                            row_selectable="single",
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": COLORS["primary"],
                                "color": "white",
                                "fontWeight": "bold",
                                "fontSize": "13px",
                                "textAlign": "center",
                            },
                            style_cell={
                                "textAlign": "center",
                                "padding": "10px 12px",
                                "fontSize": "13px",
                                "fontFamily": "'Segoe UI', sans-serif",
                                "border": "1px solid #eef2f7",
                            },
                            style_data_conditional=[
                                {"if": {"filter_query": '{risk_label} = "High"',
                                        "column_id": "risk_label"},
                                 "backgroundColor": "#fde8e8", "color": COLORS["risk_high"],
                                 "fontWeight": "bold"},
                                {"if": {"filter_query": '{risk_label} = "Medium"',
                                        "column_id": "risk_label"},
                                 "backgroundColor": "#fef5e7", "color": COLORS["risk_medium"],
                                 "fontWeight": "bold"},
                                {"if": {"filter_query": '{risk_label} = "Low"',
                                        "column_id": "risk_label"},
                                 "backgroundColor": "#e8f8f0", "color": COLORS["risk_low"],
                                 "fontWeight": "bold"},
                            ],
                        )
                    ),
                    className="graph-card",
                ),
            ], md=12),
        ], className="mb-2"),
        dbc.Row([graph_col("scorecard-radar", 5), graph_col("scorecard-perf-bar", 7)], className="g-2"),
        dbc.Row([graph_col("scorecard-scatter", 12)], className="g-2"),
    ], className="tab-page")


# ============================================================
# Page 3 — Lead Time & Forecasting
# ============================================================
def page_lead_time():
    supplier_options = [
        {"label": f"{row['supplier_id']} — {row['name']}", "value": row["supplier_id"]}
        for _, row in DATA["suppliers"].iterrows()
    ]

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Select Suppliers", className="fw-bold mb-1",
                           style={"fontSize": "13px"}),
                dcc.Dropdown(
                    id="lt-supplier-select",
                    options=supplier_options,
                    value=["SUP001", "SUP007", "SUP010"],
                    multi=True,
                    placeholder="Select suppliers...",
                ),
            ], md=12),
        ], className="mb-3"),
        dbc.Row([graph_col("lt-historical-line", 6), graph_col("lt-forecast-chart", 6)], className="g-2"),
        dbc.Row([graph_col("lt-variance-bar", 6), graph_col("lt-category-box", 6)], className="g-2"),
    ], className="tab-page")


# ============================================================
# Page 4 — Quality & Goods Receipts
# ============================================================
def page_quality():
    return html.Div([
        dbc.Row([graph_col("qual-histogram", 6), graph_col("qual-scatter", 6)], className="g-2"),
        dbc.Row([graph_col("qual-heatmap", 7), graph_col("qual-donut", 5)], className="g-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("🚨 Anomaly Flags", className="mb-2",
                                style={"color": COLORS["danger"]}),
                        html.Div(id="qual-anomaly-table"),
                    ]),
                    className="graph-card",
                ),
            ], md=12),
        ]),
    ], className="tab-page")


# ============================================================
# Page 5 — Communications & Contracts
# ============================================================
def page_communications():
    return html.Div([
        dbc.Row([graph_col("comm-response-bar", 7), graph_col("comm-sla-gauge", 5)], className="g-2"),
        dbc.Row([graph_col("comm-channel-pie", 4), graph_col("comm-contract-timeline", 8)], className="g-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("📋 Contracts Expiring Within 90 Days", className="mb-2"),
                        html.Div(id="comm-expiring-table"),
                    ]),
                    className="graph-card",
                ),
            ], md=8),
            graph_col("comm-breach-bar", 4),
        ]),
    ], className="tab-page")


# ============================================================
# App Layout
# ============================================================
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2("📦 Supplier Relationship Management", className="mb-0",
                     style={"color": COLORS["primary"], "fontWeight": "700"}),
            html.P("SCME P6 — UE23CS342BA1 | PES University",
                    style={"color": "#95a5a6", "fontSize": "14px", "marginBottom": "0"}),
        ], md=8),
        dbc.Col([
            html.Div([
                html.Span("Last Updated: ", style={"color": "#95a5a6", "fontSize": "12px"}),
                html.Span(TODAY.strftime("%d %b %Y"),
                          style={"color": COLORS["accent"], "fontWeight": "600", "fontSize": "12px"}),
            ], style={"textAlign": "right", "paddingTop": "10px"}),
        ], md=4),
    ], className="py-3 mb-3 app-header",
       style={"borderBottom": f"2px solid {COLORS['light']}"}),

    # Global Filters
    global_filters,

    # Tabs
    dcc.Tabs(
        id="main-tabs",
        value="tab-exec",
        children=[
            dcc.Tab(label="📊 Executive Overview", value="tab-exec",
                    style={"fontWeight": "600"}, selected_style={"fontWeight": "700"}),
            dcc.Tab(label="🏆 Supplier Scorecard", value="tab-scorecard",
                    style={"fontWeight": "600"}, selected_style={"fontWeight": "700"}),
            dcc.Tab(label="⏱️ Lead Time & Forecasting", value="tab-leadtime",
                    style={"fontWeight": "600"}, selected_style={"fontWeight": "700"}),
            dcc.Tab(label="🔍 Quality & Goods Receipts", value="tab-quality",
                    style={"fontWeight": "600"}, selected_style={"fontWeight": "700"}),
            dcc.Tab(label="📨 Communications & Contracts", value="tab-comms",
                    style={"fontWeight": "600"}, selected_style={"fontWeight": "700"}),
        ],
        className="mb-3 app-tabs",
    ),

    # Tab Content
    html.Div(id="tab-content"),

], fluid=True, className="app-shell", style={"backgroundColor": "#f5f7fb", "minHeight": "100vh", "paddingBottom": "18px"})


# ============================================================
# Tab Switching Callback
# ============================================================
@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value"),
)
def render_tab(tab):
    if tab == "tab-exec":
        return page_executive()
    elif tab == "tab-scorecard":
        return page_scorecard()
    elif tab == "tab-leadtime":
        return page_lead_time()
    elif tab == "tab-quality":
        return page_quality()
    elif tab == "tab-comms":
        return page_communications()
    return html.Div("Select a tab")


# ============================================================
# Reset Filters Callback
# ============================================================
@app.callback(
    [Output("date-range", "start_date"),
     Output("date-range", "end_date"),
     Output("category-filter", "value")],
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n):
    return "2023-01-01", "2026-03-31", "All"


# ============================================================
# Helper: Filter POs by date range and category
# ============================================================
def filter_pos(start_date, end_date, category):
    po = DATA["purchase_orders"].copy()
    if start_date:
        po = po[po["order_date"] >= pd.to_datetime(start_date)]
    if end_date:
        po = po[po["order_date"] <= pd.to_datetime(end_date)]
    if category and category != "All":
        po = po[po["category"] == category]
    return po


def safe_period_to_timestamp(series):
    """Safely convert a Period series to Timestamps, handling already-Timestamp series."""
    try:
        return series.dt.to_timestamp()
    except AttributeError:
        return pd.to_datetime(series.astype(str))


# ============================================================
# PAGE 1 CALLBACKS — Executive Overview
# ============================================================
@app.callback(
    [Output("exec-kpi-cards", "children"),
     Output("exec-ontime-bar", "figure"),
     Output("exec-status-pie", "figure"),
     Output("exec-monthly-line", "figure"),
     Output("exec-category-bar", "figure")],
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("category-filter", "value")],
)
def update_executive(start_date, end_date, category):
    po = filter_pos(start_date, end_date, category)
    suppliers = DATA["suppliers"]
    contracts = DATA["contracts"]
    inspections = DATA["inspections"]

    # ---- KPI Cards ----
    active_suppliers = suppliers[suppliers["is_active"] == 1].shape[0]

    completed = po[po["status"].isin(["Delivered", "Delayed"])].copy()
    completed = completed[completed["actual_delivery"].notna()].copy()
    if not completed.empty:
        completed["on_time"] = completed["actual_delivery"] <= completed["expected_delivery"]
        ontime_pct = round(completed["on_time"].mean() * 100, 1)
        completed["lead_time"] = (completed["actual_delivery"] - completed["order_date"]).dt.days
        avg_lead = round(completed["lead_time"].mean(), 1)
    else:
        ontime_pct = 0
        avg_lead = 0

    # Avg defect rate from inspections
    avg_defect = round(inspections["defect_rate_pct"].mean(), 1) if not inspections.empty else 0

    open_pos = po[po["status"] == "Pending"].shape[0]

    expiring = contracts[
        (contracts["end_date"] >= pd.Timestamp(TODAY)) &
        (contracts["end_date"] <= pd.Timestamp(TODAY + timedelta(days=30)))
    ].shape[0]

    kpi_cards = dbc.Row([
        dbc.Col(make_kpi_card("Active Suppliers", str(active_suppliers), "🏭", COLORS["accent"]), md=2),
        dbc.Col(make_kpi_card("On-Time Delivery", f"{ontime_pct}%", "✅", COLORS["success"]), md=2),
        dbc.Col(make_kpi_card("Avg Lead Time", f"{avg_lead} days", "⏱️", COLORS["primary"]), md=2),
        dbc.Col(make_kpi_card("Avg Defect Rate", f"{avg_defect}%", "⚠️", COLORS["warning"]), md=2),
        dbc.Col(make_kpi_card("Open POs", str(open_pos), "📋", COLORS["accent"]), md=2),
        dbc.Col(make_kpi_card("Contracts Expiring", str(expiring), "🔔", COLORS["danger"]), md=2),
    ], className="mb-3")

    # ---- Bar chart: Top 10 Suppliers by On-Time Delivery Rate ----
    if not completed.empty:
        supp_ontime = completed.groupby("supplier_id")["on_time"].mean().reset_index()
        supp_ontime["on_time_pct"] = (supp_ontime["on_time"] * 100).round(1)
        supp_ontime = supp_ontime.merge(
            suppliers[["supplier_id", "name"]], on="supplier_id", how="left"
        )
        top10 = supp_ontime.nlargest(10, "on_time_pct")

        fig_ontime = go.Figure()
        fig_ontime.add_trace(go.Bar(
            x=top10["on_time_pct"], y=top10["name"],
            orientation="h",
            marker_color=[COLORS["success"] if v >= 85 else COLORS["warning"] for v in top10["on_time_pct"]],
            text=top10["on_time_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
        ))
        fig_ontime.add_vline(x=85, line_dash="dash", line_color="red", line_width=2,
                             annotation_text="85% Benchmark")
        fig_ontime.update_layout(
            title="Top 10 Suppliers — On-Time Delivery Rate",
            xaxis_title="On-Time %", yaxis_title="",
            height=400, margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
        )
    else:
        fig_ontime = go.Figure()
        fig_ontime.update_layout(title="No data for selected filters", height=400)

    # ---- Pie chart: PO Status Distribution ----
    status_counts = po["status"].value_counts()
    color_map = {"Delivered": COLORS["success"], "Pending": COLORS["accent"],
                 "Delayed": COLORS["danger"], "Cancelled": "#95a5a6"}
    fig_status = go.Figure(data=[go.Pie(
        labels=status_counts.index, values=status_counts.values,
        hole=0.4,
        marker_colors=[color_map.get(s, "#ccc") for s in status_counts.index],
        textinfo="label+percent",
        textfont_size=12,
    )])
    fig_status.update_layout(
        title="PO Status Distribution",
        height=400, margin=dict(l=20, r=20, t=40, b=20),
    )

    # ---- Line chart: Monthly PO count & value ----
    po_monthly = po.copy()
    po_monthly = po_monthly[po_monthly["order_date"].notna()].copy()
    if not po_monthly.empty:
        po_monthly["year_month"] = po_monthly["order_date"].dt.to_period("M")
        monthly_agg = po_monthly.groupby("year_month").agg(
            po_count=("po_id", "count"),
            total_value=("total_value", "sum"),
        ).reset_index()
        monthly_agg["year_month"] = monthly_agg["year_month"].dt.to_timestamp()

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=monthly_agg["year_month"], y=monthly_agg["po_count"],
            name="PO Count", marker_color=COLORS["accent"], opacity=0.7,
            yaxis="y",
        ))
        fig_monthly.add_trace(go.Scatter(
            x=monthly_agg["year_month"],
            y=monthly_agg["total_value"],
            name="Total Value (₹)",
            line=dict(color=COLORS["danger"], width=2),
            yaxis="y2",
        ))
        fig_monthly.update_layout(
            title="Monthly PO Count & Value",
            xaxis_title="Month",
            yaxis=dict(title="PO Count", side="left"),
            yaxis2=dict(title="Total Value (₹)", side="right", overlaying="y"),
            height=400, margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(x=0.01, y=0.99),
            plot_bgcolor="white",
        )
    else:
        fig_monthly = go.Figure()
        fig_monthly.update_layout(title="No data for selected filters", height=400)

    # ---- Horizontal bar: Avg Lead Time by Category ----
    if not completed.empty:
        cat_lead = completed.groupby("category")["lead_time"].mean().round(1).reset_index()
        cat_lead = cat_lead.sort_values("lead_time")
        fig_cat = go.Figure(go.Bar(
            x=cat_lead["lead_time"], y=cat_lead["category"],
            orientation="h",
            marker_color=COLORS["accent"],
            text=cat_lead["lead_time"].apply(lambda x: f"{x:.1f} days"),
            textposition="auto",
        ))
        fig_cat.update_layout(
            title="Average Lead Time by Category",
            xaxis_title="Days", yaxis_title="",
            height=400, margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white",
        )
    else:
        fig_cat = go.Figure()
        fig_cat.update_layout(title="No data for selected filters", height=400)

    return kpi_cards, fig_ontime, fig_status, fig_monthly, fig_cat


# ============================================================
# PAGE 2 CALLBACKS — Supplier Scorecard
# ============================================================
@app.callback(
    Output("scorecard-radar", "figure"),
    [Input("scorecard-table", "selected_rows")],
    [State("scorecard-table", "data")],
)
def update_radar(selected_rows, table_data):
    if not selected_rows or not table_data:
        fig = go.Figure()
        fig.update_layout(
            title="Select a supplier from the table to view radar chart",
            height=400,
        )
        return fig

    row_idx = selected_rows[0]
    if row_idx >= len(table_data):
        return go.Figure()

    row = table_data[row_idx]
    supplier_name = row.get("name", "")
    supplier_cat = row.get("category", "")
    supplier_id = row.get("supplier_id", "")

    # Get supplier metrics
    risk_df = DATA["risk_scores"]
    if not supplier_id:
        fallback = risk_df[
            (risk_df["name"] == supplier_name) & (risk_df["category"] == supplier_cat)
        ]
        if fallback.empty:
            fallback = risk_df[risk_df["name"] == supplier_name]
        if not fallback.empty:
            supplier_id = fallback.iloc[0]["supplier_id"]
    supp = risk_df[risk_df["supplier_id"] == supplier_id]
    cat_avg = risk_df[risk_df["category"] == supplier_cat]

    if supp.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Supplier details unavailable for the selected row",
            height=400,
        )
        return fig

    s = supp.iloc[0]

    # Compute additional metrics for radar
    po_completed = DATA["purchase_orders"][
        (DATA["purchase_orders"]["actual_delivery"].notna()) &
        (DATA["purchase_orders"]["supplier_id"] == supplier_id)
    ].copy()

    # Responsiveness (normalize to 0-100, lower response time is better)
    comms = DATA["communications"][DATA["communications"]["supplier_id"] == supplier_id]
    resolved = comms[comms["resolved"] == "Yes"]
    resp_time = resolved["response_time_hours"].mean() if not resolved.empty else 48
    responsiveness = max(0, min(100, 100 - resp_time * 1.5))

    # Cost compliance (normalize)
    cost_compliance = max(0, min(100, 100 - abs(s.get("risk_score", 50) - 50)))

    # Fulfillment rate
    receipts = DATA["goods_receipts"].merge(
        DATA["purchase_orders"][["po_id", "supplier_id", "quantity"]],
        on="po_id", how="inner"
    )
    supp_receipts = receipts[receipts["supplier_id"] == supplier_id]
    total_qty = supp_receipts["quantity"].sum() if not supp_receipts.empty else 0
    if total_qty > 0:
        fulfillment = min(100, (supp_receipts["received_quantity"].sum() / total_qty) * 100)
    else:
        fulfillment = 90

    # Compute category averages
    cat_on_time = cat_avg["on_time_rate"].mean() if not cat_avg.empty else 70
    cat_quality = max(0, 100 - cat_avg["avg_defect_rate"].mean() * 5) if not cat_avg.empty else 70

    categories = ["Delivery Reliability", "Quality", "Responsiveness",
                   "Cost Compliance", "Fulfillment Rate"]
    supplier_vals = [
        s["on_time_rate"],
        max(0, 100 - s["avg_defect_rate"] * 5),
        responsiveness,
        cost_compliance,
        fulfillment,
    ]
    cat_avg_vals = [cat_on_time, cat_quality, 60, 65, 90]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=supplier_vals + [supplier_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=supplier_name,
        fillcolor="rgba(52, 152, 219, 0.3)",
        line=dict(color=COLORS["accent"], width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=cat_avg_vals + [cat_avg_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=f"{supplier_cat} Avg",
        fillcolor="rgba(149, 165, 166, 0.2)",
        line=dict(color="#95a5a6", width=1, dash="dash"),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=f"Scorecard — {supplier_name}",
        height=400, margin=dict(l=40, r=40, t=60, b=20),
        legend=dict(x=0.0, y=-0.2, orientation="h"),
    )
    return fig


@app.callback(
    Output("scorecard-perf-bar", "figure"),
    [Input("date-range", "start_date")],  # Trigger on load
)
def update_perf_bar(_):
    risk_df = DATA["risk_scores"]
    if risk_df.empty:
        return go.Figure()

    # Compute performance score
    risk_df = risk_df.copy()
    risk_df["perf_score"] = (
        risk_df["on_time_rate"] * 0.30 +
        (100 - risk_df["avg_defect_rate"]) * 0.30 +
        (100 - risk_df["risk_score"]) * 0.40
    ).round(1)

    risk_df = risk_df.sort_values("perf_score", ascending=True)

    color_map = {"High": COLORS["risk_high"], "Medium": COLORS["risk_medium"],
                 "Low": COLORS["risk_low"]}
    colors = [color_map.get(r, "#ccc") for r in risk_df["risk_label"]]

    fig = go.Figure(go.Bar(
        x=risk_df["perf_score"], y=risk_df["name"],
        orientation="h",
        marker_color=colors,
        text=risk_df["perf_score"].apply(lambda x: f"{x:.0f}"),
        textposition="auto",
    ))
    fig.update_layout(
        title="Supplier Performance Score (Ranked)",
        xaxis_title="Performance Score", yaxis_title="",
        height=max(400, len(risk_df) * 22),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )
    return fig


@app.callback(
    Output("scorecard-scatter", "figure"),
    [Input("date-range", "start_date")],
)
def update_scorecard_scatter(_):
    risk_df = DATA["risk_scores"]
    if risk_df.empty:
        return go.Figure()

    # Get total PO value per supplier
    po = DATA["purchase_orders"]
    supp_value = po.groupby("supplier_id")["total_value"].sum().reset_index()
    plot_df = risk_df.merge(supp_value, on="supplier_id", how="left")
    plot_df["total_value"] = plot_df["total_value"].fillna(100000)

    color_map = {"High": COLORS["risk_high"], "Medium": COLORS["risk_medium"],
                 "Low": COLORS["risk_low"]}

    fig = go.Figure()
    for label in ["Low", "Medium", "High"]:
        subset = plot_df[plot_df["risk_label"] == label]
        fig.add_trace(go.Scatter(
            x=subset["on_time_rate"], y=subset["avg_defect_rate"],
            mode="markers",
            marker=dict(
                size=np.sqrt(subset["total_value"]) / 80,
                color=color_map[label],
                opacity=0.7,
                line=dict(width=1, color="white"),
            ),
            text=subset["name"],
            name=label,
            hovertemplate="%{text}<br>On-Time: %{x:.1f}%<br>Defect: %{y:.1f}%<extra></extra>",
        ))

    # Quadrant lines
    fig.add_hline(y=5, line_dash="dash", line_color="#95a5a6", line_width=1)
    fig.add_vline(x=85, line_dash="dash", line_color="#95a5a6", line_width=1)

    # Quadrant labels
    fig.add_annotation(x=95, y=1, text="Champions", showarrow=False,
                       font=dict(color=COLORS["success"], size=12, family="Arial Black"))
    fig.add_annotation(x=60, y=1, text="Delivery Risk", showarrow=False,
                       font=dict(color=COLORS["warning"], size=12, family="Arial Black"))
    fig.add_annotation(x=95, y=20, text="Quality Risk", showarrow=False,
                       font=dict(color=COLORS["warning"], size=12, family="Arial Black"))
    fig.add_annotation(x=60, y=20, text="Critical", showarrow=False,
                       font=dict(color=COLORS["danger"], size=12, family="Arial Black"))

    fig.update_layout(
        title="Supplier Quadrant — On-Time Rate vs Defect Rate",
        xaxis_title="On-Time Delivery Rate (%)",
        yaxis_title="Defect Rate (%)",
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )
    return fig


# ============================================================
# PAGE 3 CALLBACKS — Lead Time & Forecasting
# BUG FIX: Use ALL purchase orders (not category-filtered) for supplier-specific
#          lead time charts. Category filter only applies to variance + box charts.
# ============================================================
@app.callback(
    [Output("lt-historical-line", "figure"),
     Output("lt-forecast-chart", "figure"),
     Output("lt-variance-bar", "figure"),
     Output("lt-category-box", "figure")],
    [Input("lt-supplier-select", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("category-filter", "value")],
)
def update_lead_time(selected_suppliers, start_date, end_date, category):
    if isinstance(selected_suppliers, str):
        selected_suppliers = [selected_suppliers]
    if not selected_suppliers:
        selected_suppliers = []

    suppliers = DATA["suppliers"]

    # --- Use ALL POs (date-filtered only) for historical & forecast lines ---
    # so that supplier-specific charts work regardless of category filter
    all_po = DATA["purchase_orders"].copy()
    if start_date:
        all_po = all_po[all_po["order_date"] >= pd.to_datetime(start_date)]
    if end_date:
        all_po = all_po[all_po["order_date"] <= pd.to_datetime(end_date)]

    all_completed = all_po[all_po["actual_delivery"].notna()].copy()
    all_completed["lead_time"] = (
        all_completed["actual_delivery"] - all_completed["order_date"]
    ).dt.days
    all_completed = all_completed[all_completed["lead_time"] > 0]

    # --- Category-filtered POs for variance + box charts ---
    po = filter_pos(start_date, end_date, category)
    completed = po[po["actual_delivery"].notna()].copy()
    if not completed.empty:
        completed["lead_time"] = (
            completed["actual_delivery"] - completed["order_date"]
        ).dt.days
        completed = completed[completed["lead_time"] > 0]

    # ---- Historical Line: Monthly avg lead time per selected supplier ----
    fig_hist = go.Figure()
    if selected_suppliers and not all_completed.empty:
        for sid in selected_suppliers:
            sid_data = all_completed[all_completed["supplier_id"] == sid].copy()
            if sid_data.empty:
                continue
            sid_data = sid_data[sid_data["order_date"].notna()].copy()
            sid_data["year_month"] = sid_data["order_date"].dt.to_period("M")
            monthly = sid_data.groupby("year_month")["lead_time"].mean().reset_index()
            monthly["year_month"] = monthly["year_month"].dt.to_timestamp()
            monthly = monthly.sort_values("year_month")

            name_row = suppliers[suppliers["supplier_id"] == sid]["name"].values
            name = name_row[0] if len(name_row) > 0 else sid

            fig_hist.add_trace(go.Scatter(
                x=monthly["year_month"],
                y=monthly["lead_time"],
                mode="lines+markers",
                name=name,
                line=dict(width=2),
            ))

    fig_hist.update_layout(
        title="Historical Monthly Average Lead Time",
        xaxis_title="Month",
        yaxis_title="Lead Time (days)",
        xaxis=dict(type="date"),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
        legend=dict(x=0, y=1),
    )

    # ---- Forecast Chart ----
    fig_forecast = go.Figure()
    predictions = DATA["predictions"]

    if not predictions.empty and selected_suppliers:
        for sid in selected_suppliers:
            name_row = suppliers[suppliers["supplier_id"] == sid]["name"].values
            supplier_name = name_row[0] if len(name_row) > 0 else sid

            # Historical for this supplier
            sid_data = all_completed[all_completed["supplier_id"] == sid].copy()
            if not sid_data.empty:
                sid_data = sid_data[sid_data["order_date"].notna()].copy()
                sid_data["year_month"] = sid_data["order_date"].dt.to_period("M")
                monthly_hist = sid_data.groupby("year_month")["lead_time"].mean().reset_index()
                monthly_hist["year_month"] = monthly_hist["year_month"].dt.to_timestamp()
                monthly_hist = monthly_hist.sort_values("year_month")

                fig_forecast.add_trace(go.Scatter(
                    x=monthly_hist["year_month"],
                    y=monthly_hist["lead_time"],
                    mode="lines",
                    name=f"{supplier_name} (Historical)",
                    line=dict(width=2),
                ))

            # Forecast for this supplier
            sid_pred = predictions[predictions["supplier_id"] == sid].copy()
            if not sid_pred.empty:
                # Ensure month column is datetime
                if not pd.api.types.is_datetime64_any_dtype(sid_pred["month"]):
                    sid_pred["month"] = pd.to_datetime(sid_pred["month"], errors="coerce")
                sid_pred = sid_pred.dropna(subset=["month"]).sort_values("month")
                pred_dates = sid_pred["month"]

                fig_forecast.add_trace(go.Scatter(
                    x=pred_dates,
                    y=sid_pred["predicted_lead_time_days"],
                    mode="lines+markers",
                    name=f"{supplier_name} (Forecast)",
                    line=dict(width=2, dash="dash"),
                ))

                # Confidence interval
                if {"upper_95", "lower_95"}.issubset(sid_pred.columns):
                    x_combined = pd.concat([pred_dates, pred_dates.iloc[::-1]])
                    y_combined = pd.concat([sid_pred["upper_95"], sid_pred["lower_95"].iloc[::-1]])
                    fig_forecast.add_trace(go.Scatter(
                        x=x_combined,
                        y=y_combined,
                        fill="toself",
                        fillcolor="rgba(52,152,219,0.1)",
                        line=dict(color="rgba(52,152,219,0)"),
                        showlegend=False,
                        name="95% CI",
                    ))

    fig_forecast.update_layout(
        title="Lead Time Forecast (3-Month Ahead with 95% CI)",
        xaxis_title="Month",
        yaxis_title="Lead Time (days)",
        xaxis=dict(type="date"),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )

    # ---- Variance Bar (uses category-filtered data) ----
    # Use all_completed for variance so it's not empty when a specific category is set
    # and none of the selected suppliers belong to it
    variance_source = all_completed if completed.empty else completed

    if not variance_source.empty:
        variance = variance_source.groupby("supplier_id")["lead_time"].std().reset_index()
        variance.columns = ["supplier_id", "lt_variance"]
        variance = variance.dropna().sort_values("lt_variance", ascending=False)
        variance = variance.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")

        # Filter to suppliers in the selected category if a category filter is active
        if category and category != "All":
            cat_suppliers = suppliers[suppliers["category"] == category]["supplier_id"].tolist()
            variance = variance[variance["supplier_id"].isin(cat_suppliers)]

        colors = [COLORS["danger"] if v > 7 else COLORS["accent"] for v in variance["lt_variance"]]
        fig_var = go.Figure(go.Bar(
            x=variance["lt_variance"].round(1),
            y=variance["name"],
            orientation="h",
            marker_color=colors,
            text=variance["lt_variance"].round(1),
            textposition="auto",
        ))
        fig_var.add_vline(x=7, line_dash="dash", line_color="red",
                         annotation_text="High Unpredictability (>7 days)")
        fig_var.update_layout(
            title="Lead Time Variance by Supplier",
            xaxis_title="Std Dev (days)",
            yaxis_title="",
            height=max(400, len(variance) * 22),
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
        )
    else:
        fig_var = go.Figure()
        fig_var.update_layout(title="No data for selected filters", height=400)

    # ---- Box Plot: Lead Time by Category (always uses all date-filtered POs) ----
    if not all_completed.empty:
        fig_box = go.Figure()
        for cat in CATEGORIES:
            cat_data = all_completed[all_completed["category"] == cat]["lead_time"]
            if not cat_data.empty:
                fig_box.add_trace(go.Box(y=cat_data, name=cat))
        fig_box.update_layout(
            title="Lead Time Distribution by Material Category",
            yaxis_title="Lead Time (days)",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white",
        )
    else:
        fig_box = go.Figure()
        fig_box.update_layout(title="No data for selected filters", height=400)

    return fig_hist, fig_forecast, fig_var, fig_box


# ============================================================
# PAGE 4 CALLBACKS — Quality & Goods Receipts
# ============================================================
@app.callback(
    [Output("qual-histogram", "figure"),
     Output("qual-scatter", "figure"),
     Output("qual-heatmap", "figure"),
     Output("qual-donut", "figure"),
     Output("qual-anomaly-table", "children")],
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("category-filter", "value")],
)
def update_quality(start_date, end_date, category):
    inspections = DATA["inspections"].copy()
    po = filter_pos(start_date, end_date, category)
    receipts = DATA["goods_receipts"]
    suppliers = DATA["suppliers"]
    anomalies = DATA["anomalies"]

    # Filter inspections to match filtered POs
    receipt_ids = receipts[receipts["po_id"].isin(po["po_id"])]["receipt_id"]
    filtered_insp = inspections[inspections["receipt_id"].isin(receipt_ids)]

    # ---- Histogram: Defect Rate Distribution ----
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=filtered_insp["defect_rate_pct"], nbinsx=50,
        marker_color=COLORS["accent"], opacity=0.8,
        name="Inspections",
    ))
    fig_hist.add_vline(x=5, line_dash="dash", line_color="orange", line_width=2,
                       annotation_text="5% Acceptable")
    fig_hist.add_vline(x=10, line_dash="dash", line_color="red", line_width=2,
                       annotation_text="10% Critical")
    fig_hist.update_layout(
        title="Defect Rate Distribution",
        xaxis_title="Defect Rate (%)", yaxis_title="Count",
        height=400, margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )

    # ---- Scatter: Defect Rate vs Delay ----
    insp_po = filtered_insp.merge(receipts[["receipt_id", "po_id"]], on="receipt_id", how="left")
    insp_po = insp_po.merge(
        po[["po_id", "supplier_id", "category", "quantity", "expected_delivery", "actual_delivery"]],
        on="po_id", how="inner"
    )
    insp_po = insp_po[insp_po["actual_delivery"].notna() & insp_po["expected_delivery"].notna()].copy()
    insp_po["delay_days"] = (insp_po["actual_delivery"] - insp_po["expected_delivery"]).dt.days

    if not insp_po.empty:
        fig_scat = px.scatter(
            insp_po, x="delay_days", y="defect_rate_pct",
            color="category", size="quantity",
            hover_data=["supplier_id"],
            title="Defect Rate vs Delivery Delay",
            labels={"delay_days": "Delivery Delay (days)", "defect_rate_pct": "Defect Rate (%)"},
            height=400,
        )
        fig_scat.update_layout(margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="white")
    else:
        fig_scat = go.Figure()
        fig_scat.update_layout(title="No data for selected filters", height=400)

    # ---- Heatmap: Defect Rate by Supplier × Month ----
    if not filtered_insp.empty and not insp_po.empty:
        insp_supp = insp_po.copy()
        insp_supp = insp_supp.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")
        insp_supp["month"] = insp_supp["inspection_date"].dt.to_period("M").astype(str)

        top15_worst = insp_supp.groupby("name")["defect_rate_pct"].mean().nlargest(15).index.tolist()
        heatmap_data = insp_supp[insp_supp["name"].isin(top15_worst)]
        if not heatmap_data.empty:
            pivot = heatmap_data.pivot_table(
                values="defect_rate_pct", index="name", columns="month", aggfunc="mean"
            ).fillna(0)

            fig_heat = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale="RdYlGn_r",
                text=np.round(pivot.values, 1),
                texttemplate="%{text}",
                colorbar_title="Defect %",
            ))
            fig_heat.update_layout(
                title="Defect Rate Heatmap — Top 15 Worst Suppliers",
                xaxis_title="Month", yaxis_title="",
                height=450, margin=dict(l=20, r=20, t=40, b=20),
            )
        else:
            fig_heat = go.Figure()
            fig_heat.update_layout(title="No data for heatmap", height=450)
    else:
        fig_heat = go.Figure()
        fig_heat.update_layout(title="No data for selected filters", height=450)

    # ---- Donut: Inspection Result Breakdown ----
    result_counts = filtered_insp["inspection_result"].value_counts()
    color_map = {"Pass": COLORS["success"], "Fail": COLORS["danger"], "Conditional": COLORS["warning"]}
    if not result_counts.empty:
        fig_donut = go.Figure(data=[go.Pie(
            labels=result_counts.index, values=result_counts.values,
            hole=0.5,
            marker_colors=[color_map.get(r, "#ccc") for r in result_counts.index],
            textinfo="label+percent",
        )])
    else:
        fig_donut = go.Figure()
    fig_donut.update_layout(
        title="Inspection Results Breakdown",
        height=450, margin=dict(l=20, r=20, t=40, b=20),
    )

    # ---- Anomaly Table ----
    if not anomalies.empty:
        anom = anomalies[anomalies["is_anomaly"] == 1].copy()
        anom = anom.sort_values("anomaly_score", ascending=False)
        # Only show columns that exist
        desired_cols = ["receipt_id", "supplier_name", "received_date",
                        "defect_rate_pct", "fulfillment_ratio",
                        "delivery_delay_days", "anomaly_score"]
        existing_cols = [c for c in desired_cols if c in anom.columns]
        anom_display = anom[existing_cols].head(20)
        col_rename = {
            "receipt_id": "Receipt ID", "supplier_name": "Supplier",
            "received_date": "Date", "defect_rate_pct": "Defect %",
            "fulfillment_ratio": "Fulfillment", "delivery_delay_days": "Delay Days",
            "anomaly_score": "Anomaly Score",
        }
        anom_display = anom_display.rename(columns={k: v for k, v in col_rename.items() if k in anom_display.columns})

        anomaly_table = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in anom_display.columns],
            data=anom_display.to_dict("records"),
            style_header={
                "backgroundColor": COLORS["danger"],
                "color": "white", "fontWeight": "bold",
            },
            style_cell={"textAlign": "center", "padding": "6px", "fontSize": "13px"},
            style_data_conditional=[
                {"if": {"filter_query": "{Anomaly Score} > 0.3"},
                 "backgroundColor": "#fde8e8"},
            ],
            page_size=10,
        )
    else:
        anomaly_table = html.P("No anomaly data available. Run models.py first.")

    return fig_hist, fig_scat, fig_heat, fig_donut, anomaly_table


# ============================================================
# PAGE 5 CALLBACKS — Communications & Contracts
# ============================================================
@app.callback(
    [Output("comm-response-bar", "figure"),
     Output("comm-sla-gauge", "figure"),
     Output("comm-channel-pie", "figure"),
     Output("comm-contract-timeline", "figure"),
     Output("comm-expiring-table", "children"),
     Output("comm-breach-bar", "figure")],
    [Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("category-filter", "value")],
)
def update_comms(start_date, end_date, category):
    comms = DATA["communications"].copy()
    contracts = DATA["contracts"].copy()
    suppliers = DATA["suppliers"]
    po = filter_pos(start_date, end_date, category)

    # Filter comms by date
    if start_date:
        comms = comms[comms["comm_date"] >= pd.to_datetime(start_date)]
    if end_date:
        comms = comms[comms["comm_date"] <= pd.to_datetime(end_date)]

    # ---- Bar: Avg Response Time per Supplier (Top 10 worst) ----
    resolved = comms[comms["resolved"] == "Yes"]
    avg_resp = resolved.groupby("supplier_id")["response_time_hours"].mean().reset_index()
    avg_resp = avg_resp.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")
    avg_resp = avg_resp.nlargest(10, "response_time_hours").sort_values("response_time_hours")

    fig_resp = go.Figure(go.Bar(
        x=avg_resp["response_time_hours"].round(1),
        y=avg_resp["name"],
        orientation="h",
        marker_color=[COLORS["danger"] if v > 24 else COLORS["accent"]
                     for v in avg_resp["response_time_hours"]],
        text=avg_resp["response_time_hours"].round(1).apply(lambda x: f"{x:.1f} hrs"),
        textposition="auto",
    ))
    fig_resp.add_vline(x=24, line_dash="dash", line_color="red",
                       annotation_text="24hr SLA")
    fig_resp.update_layout(
        title="Top 10 Worst Responders — Avg Response Time",
        xaxis_title="Hours", yaxis_title="",
        height=400, margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )

    # ---- Gauge: Overall SLA Compliance ----
    resolved_comms = comms[comms["resolved"] == "Yes"]
    if not resolved_comms.empty:
        sla_compliant = (resolved_comms["response_time_hours"] <= 24).sum()
        sla_pct = round(sla_compliant / len(resolved_comms) * 100, 1)
    else:
        sla_pct = 0

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sla_pct,
        title={"text": "SLA Compliance %", "font": {"size": 16}},
        delta={"reference": 90, "increasing": {"color": COLORS["success"]}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["accent"]},
            "steps": [
                {"range": [0, 60], "color": "#fde8e8"},
                {"range": [60, 80], "color": "#fef5e7"},
                {"range": [80, 100], "color": "#e8f8f0"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.8,
                "value": 90,
            },
        },
    ))
    fig_gauge.update_layout(height=400, margin=dict(l=40, r=40, t=60, b=20))

    # ---- Pie: Channel Breakdown ----
    channel_counts = comms["channel"].value_counts()
    fig_channel = go.Figure(data=[go.Pie(
        labels=channel_counts.index, values=channel_counts.values,
        hole=0.35,
        textinfo="label+percent",
    )])
    fig_channel.update_layout(
        title="Communication Channel Distribution",
        height=400, margin=dict(l=20, r=20, t=40, b=20),
    )

    # ---- Timeline: Contract Gantt Chart ----
    ct = contracts.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")
    ct = ct[ct["start_date"].notna() & ct["end_date"].notna()].copy()
    ct = ct.sort_values("end_date")

    color_map = {
        "Active": COLORS["success"], "Expired": "#95a5a6",
        "Renewed": COLORS["accent"], "Under Review": COLORS["warning"],
    }

    fig_timeline = go.Figure()

    for idx, (_, row) in enumerate(ct.iterrows()):
        color = color_map.get(row["renewal_status"], "#ccc")
        start_dt = pd.Timestamp(row["start_date"])
        end_dt = pd.Timestamp(row["end_date"])
        days_to_expiry = int((end_dt - pd.Timestamp(TODAY)) / pd.Timedelta(days=1))

        fig_timeline.add_trace(go.Scatter(
            x=[start_dt, end_dt],
            y=[row["name"], row["name"]],
            mode="lines",
            line=dict(color=color, width=16),
            name=row["renewal_status"],
            showlegend=False,
            hovertemplate=(
                f"{row['name']}<br>"
                f"Status: {row['renewal_status']}<br>"
                f"Start: {start_dt.strftime('%Y-%m-%d')}<br>"
                f"End: {end_dt.strftime('%Y-%m-%d')}<extra></extra>"
            ),
        ))

        if 0 < days_to_expiry <= 30:
            fig_timeline.add_trace(go.Scatter(
                x=[end_dt], y=[row["name"]],
                mode="markers",
                marker=dict(size=12, color="orange", symbol="diamond"),
                showlegend=False,
                hovertemplate=f"⚠️ Expiring in {days_to_expiry} days<extra></extra>",
            ))

    today_ts = pd.Timestamp(TODAY)
    fig_timeline.add_shape(
        type="line", x0=today_ts, x1=today_ts, y0=0, y1=1,
        yref="paper", line=dict(color="red", width=2, dash="solid"),
    )
    fig_timeline.add_annotation(
        x=today_ts, y=1.02, yref="paper",
        text="Today", showarrow=False,
        font=dict(color="red", size=12, family="Arial Black"),
    )
    fig_timeline.update_layout(
        title="Contract Timeline — All Suppliers",
        xaxis_title="Date",
        xaxis=dict(type="date"),
        height=max(500, len(ct) * 25),
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
    )

    # ---- Table: Contracts Expiring Within 90 Days ----
    expiring_90 = contracts[
        (contracts["end_date"] >= pd.Timestamp(TODAY)) &
        (contracts["end_date"] <= pd.Timestamp(TODAY + timedelta(days=90)))
    ].copy()
    expiring_90 = expiring_90.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")
    expiring_90["days_left"] = (
        (expiring_90["end_date"] - pd.Timestamp(TODAY)) / pd.Timedelta(days=1)
    ).astype(int)
    expiring_90 = expiring_90.sort_values("days_left")

    exp_display = expiring_90[["name", "value_inr", "end_date", "sla_lead_time_days",
                                "renewal_status", "days_left"]].copy()
    exp_display.columns = ["Supplier", "Contract Value (₹)", "End Date",
                            "SLA Lead Time (days)", "Status", "Days Left"]
    exp_display["Contract Value (₹)"] = exp_display["Contract Value (₹)"].apply(
        lambda x: f"₹{x:,.0f}"
    )
    exp_display["End Date"] = exp_display["End Date"].dt.strftime("%Y-%m-%d")

    expiring_table = dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in exp_display.columns],
        data=exp_display.to_dict("records"),
        style_table={"overflowX": "auto", "minWidth": "100%"},
        style_header={
            "backgroundColor": COLORS["primary"],
            "color": "white", "fontWeight": "bold",
            "textAlign": "center",
            "fontSize": "13px",
            "padding": "10px 8px",
        },
        style_cell={
            "textAlign": "center",
            "padding": "9px 8px",
            "fontSize": "13px",
            "minWidth": "92px",
            "width": "92px",
            "maxWidth": "180px",
            "whiteSpace": "normal",
            "height": "auto",
            "border": "1px solid #eef2f7",
        },
        style_cell_conditional=[
            {"if": {"column_id": "Supplier"}, "minWidth": "160px", "width": "160px"},
            {"if": {"column_id": "Contract Value (₹)"}, "minWidth": "120px", "width": "120px"},
            {"if": {"column_id": "SLA Lead Time (days)"}, "minWidth": "135px", "width": "135px"},
            {"if": {"column_id": "Status"}, "minWidth": "95px", "width": "95px"},
            {"if": {"column_id": "Days Left"}, "minWidth": "85px", "width": "85px"},
        ],
        style_data_conditional=[
            {"if": {"filter_query": "{Days Left} <= 30"},
             "backgroundColor": "#fde8e8", "fontWeight": "bold"},
        ],
        page_size=10,
    )

    # ---- Bar: SLA Breach Count per Supplier (Top 15) ----
    completed_po = po[po["actual_delivery"].notna()].copy()
    if not completed_po.empty:
        completed_po["breach"] = (
            completed_po["actual_delivery"] > completed_po["expected_delivery"]
        ).astype(int)
        breach_counts = completed_po.groupby("supplier_id")["breach"].sum().reset_index()
        breach_counts = breach_counts.merge(suppliers[["supplier_id", "name"]], on="supplier_id", how="left")
        breach_counts = breach_counts.nlargest(15, "breach").sort_values("breach")

        fig_breach = go.Figure(go.Bar(
            x=breach_counts["breach"], y=breach_counts["name"],
            orientation="h",
            marker_color=COLORS["danger"],
            text=breach_counts["breach"],
            textposition="auto",
        ))
    else:
        fig_breach = go.Figure()

    fig_breach.update_layout(
        title="SLA Breach Count — Top 15 Suppliers",
        xaxis_title="Breaches", yaxis_title="",
        height=430,
        margin=dict(l=6, r=10, t=45, b=28),
        plot_bgcolor="white",
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        xaxis=dict(dtick=1, automargin=True),
    )

    return fig_resp, fig_gauge, fig_channel, fig_timeline, expiring_table, fig_breach


# ============================================================
# Run Server
# ============================================================
if __name__ == "__main__":
    app.run(debug=False, port=8050)