"""
SCME P6 — Supplier Relationship Management
Data Generator: Creates realistic synthetic data for all 6 tables.
Outputs: 6 CSV files + scm_p6.db (SQLite)

Run: python generate_data.py
"""

import random
import sqlite3
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

# ============================================================
# Reproducibility
# ============================================================
random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

# ============================================================
# Configuration
# ============================================================
NUM_SUPPLIERS = 30
NUM_POS = 500
NUM_COMMUNICATIONS = 420
CATEGORIES = ["Raw Materials", "Packaging", "Electronics", "Logistics", "MRO"]
COUNTRIES = ["India", "China", "Germany", "USA", "Vietnam", "Japan"]
CITIES = {
    "India": ["Mumbai", "Bangalore", "Chennai", "Delhi", "Pune"],
    "China": ["Shanghai", "Shenzhen", "Beijing", "Guangzhou"],
    "Germany": ["Munich", "Berlin", "Hamburg", "Frankfurt"],
    "USA": ["New York", "Chicago", "Houston", "San Jose"],
    "Vietnam": ["Ho Chi Minh City", "Hanoi", "Da Nang"],
    "Japan": ["Tokyo", "Osaka", "Nagoya", "Yokohama"],
}
PAYMENT_TERMS = ["Net30", "Net60", "Net90"]
MATERIALS = {
    "Raw Materials": ["Steel Sheets", "Copper Wire", "Aluminum Rods", "Rubber Compound", "Plastic Granules",
                      "Carbon Fiber", "Glass Panels", "Zinc Alloy", "Silicon Wafers", "Titanium Bars"],
    "Packaging": ["Corrugated Boxes", "Shrink Wrap", "Bubble Wrap", "Packing Tape", "Foam Inserts",
                  "Pallets", "Stretch Film", "Carton Boxes", "Poly Bags", "Edge Protectors"],
    "Electronics": ["PCB Boards", "Capacitors", "Resistors", "LED Modules", "Microcontrollers",
                    "Sensors", "Transistors", "Connectors", "Relays", "Transformers"],
    "Logistics": ["Freight Services", "Warehousing", "Last-Mile Delivery", "Cold Chain Transport",
                  "Cross-Docking", "Customs Clearance", "Route Optimization", "Fleet Maintenance"],
    "MRO": ["Lubricants", "Safety Gear", "Hand Tools", "Cleaning Supplies", "Spare Parts",
            "Filters", "Bearings", "Welding Rods", "Fasteners", "Electrical Tape"],
}
WAREHOUSES = ["WH-North", "WH-South", "WH-East", "WH-West", "WH-Central"]
INSPECTORS = ["R. Sharma", "A. Patel", "K. Nguyen", "M. Weber", "S. Tanaka",
              "J. Smith", "L. Chen", "P. Kumar", "D. Müller", "T. Yamamoto"]
DEFECT_TYPES = ["Dimensional", "Surface", "Functional", "Missing", "Other"]
CHANNELS = ["Email", "Call", "Meeting", "Portal"]
PRIORITIES = ["Low", "Normal", "High", "Critical"]
COMM_SUBJECTS = [
    "Delivery Status Update", "Quality Concern", "Price Renegotiation",
    "Contract Renewal Discussion", "Shipment Delay Notification",
    "Invoice Discrepancy", "New Order Requirements", "SLA Review Meeting",
    "Material Specification Change", "Urgent Stock Request",
    "Payment Terms Discussion", "Compliance Audit Follow-up",
    "Capacity Planning", "Emergency Supply Request", "Feedback on Last Shipment",
]

# Supplier profiles: (supplier_id) -> behavior
BAD_SUPPLIERS = {"SUP007", "SUP014", "SUP021"}
GOOD_SUPPLIERS = {"SUP001", "SUP003"}
IMPROVING_SUPPLIER = "SUP010"

# Date range for POs: Jan 2023 to Mar 2026
PO_START_DATE = datetime(2023, 1, 1)
PO_END_DATE = datetime(2026, 3, 31)
TOTAL_DAYS = (PO_END_DATE - PO_START_DATE).days


# ============================================================
# Helper Functions
# ============================================================
def random_date(start, end):
    """Return a random date between start and end."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))


def get_supplier_behavior(supplier_id, order_date=None):
    """Return delay and defect parameters based on supplier profile."""
    if supplier_id in BAD_SUPPLIERS:
        return {
            "delay_prob": random.uniform(0.60, 0.70),
            "delay_days_range": (3, 18),
            "defect_rate_range": (18.0, 30.0),
            "response_time_range": (72, 120),
        }
    elif supplier_id in GOOD_SUPPLIERS:
        return {
            "delay_prob": random.uniform(0.02, 0.05),
            "delay_days_range": (1, 2),
            "defect_rate_range": (0.1, 2.0),
            "response_time_range": (1, 4),
        }
    elif supplier_id == IMPROVING_SUPPLIER and order_date:
        # Improving trend: defect rate drops from 12% to 3% over 3+ years
        months_elapsed = (order_date.year - 2023) * 12 + (order_date.month - 1)
        total_months = 38  # Jan 2023 to Mar 2026
        progress = min(months_elapsed / total_months, 1.0)
        current_defect_high = 12.0 - (9.0 * progress)  # 12% -> 3%
        current_defect_low = max(current_defect_high - 2.0, 0.5)
        delay_prob = 0.40 - (0.25 * progress)  # 40% -> 15%
        return {
            "delay_prob": delay_prob,
            "delay_days_range": (1, max(2, int(8 - 5 * progress))),
            "defect_rate_range": (current_defect_low, current_defect_high),
            "response_time_range": (8, 24),
        }
    else:
        # Normal suppliers
        return {
            "delay_prob": random.uniform(0.15, 0.35),
            "delay_days_range": (1, 8),
            "defect_rate_range": (1.0, 8.0),
            "response_time_range": (4, 36),
        }


def get_raw_material_price(base_price, order_date):
    """Apply ~8% annual price drift for Raw Materials."""
    years_elapsed = (order_date - PO_START_DATE).days / 365.25
    drift = 1.0 + 0.08 * years_elapsed
    return round(base_price * drift * random.uniform(0.95, 1.05), 2)


# ============================================================
# Generate Suppliers
# ============================================================
def generate_suppliers():
    """Generate 30 suppliers across 5 categories."""
    suppliers = []
    supplier_names = [
        # Raw Materials (SUP001-SUP006)
        "SteelCraft Industries", "CopperPoint Metals", "AlumTech Global",
        "RubberKing Compounds", "PlastiFlow Materials", "CarbonEdge Ltd",
        # Packaging (SUP007-SUP012)
        "PackRight Solutions", "WrapMaster Inc", "BoxWorks International",
        "FoamSeal Corp", "PalletPro Logistics", "StretchGuard Packaging",
        # Electronics (SUP013-SUP018)
        "CircuitVault Electronics", "ChipNova Technologies", "SensorDynamics GmbH",
        "ConnectX Components", "MicroPulse Systems", "SiliconBridge Inc",
        # Logistics (SUP019-SUP024)
        "SwiftFreight Logistics", "WareHouse Pro", "LastMile Express",
        "ColdChain Solutions", "CrossDock Systems", "CustomsClear Agency",
        # MRO (SUP025-SUP030)
        "SafetyFirst Supplies", "ToolMaster Hardware", "LubeWorks Industrial",
        "SpareMax Components", "FilterTech Solutions", "WeldRight Corp",
    ]

    for i in range(NUM_SUPPLIERS):
        sid = f"SUP{i+1:03d}"
        cat_idx = i // 6
        category = CATEGORIES[cat_idx]
        country = random.choice(COUNTRIES)
        city = random.choice(CITIES[country])

        # Contract dates
        contract_start = random_date(datetime(2022, 1, 1), datetime(2023, 6, 1))
        contract_end = contract_start + timedelta(days=random.randint(365 * 2, 365 * 5))

        suppliers.append({
            "supplier_id": sid,
            "name": supplier_names[i],
            "category": category,
            "country": country,
            "city": city,
            "contact_email": f"contact@{supplier_names[i].lower().replace(' ', '').replace('.', '')}.com",
            "contact_phone": fake.phone_number(),
            "contract_start": contract_start.strftime("%Y-%m-%d"),
            "contract_end": contract_end.strftime("%Y-%m-%d"),
            "payment_terms": random.choice(PAYMENT_TERMS),
            "baseline_price_index": round(random.uniform(80, 150), 2),
            "is_active": 1 if sid != "SUP006" else 0,  # One inactive supplier
        })

    return pd.DataFrame(suppliers)


# ============================================================
# Generate Purchase Orders
# ============================================================
def generate_purchase_orders(suppliers_df):
    """Generate 500 purchase orders with seasonal patterns and supplier behaviors."""
    purchase_orders = []
    supplier_ids = suppliers_df["supplier_id"].tolist()
    supplier_categories = dict(zip(suppliers_df["supplier_id"], suppliers_df["category"]))
    supplier_baselines = dict(zip(suppliers_df["supplier_id"], suppliers_df["baseline_price_index"]))

    # Generate order dates with Q3 seasonal spike (40% more POs in Jul-Sep)
    order_dates = []
    while len(order_dates) < NUM_POS:
        d = PO_START_DATE + timedelta(days=random.randint(0, TOTAL_DAYS))
        # Q3 spike: accept Q3 dates more readily
        if d.month in [7, 8, 9]:
            order_dates.append(d)
        elif random.random() < 0.72:  # Accept ~72% of non-Q3 dates to get ~40% more in Q3
            order_dates.append(d)

    order_dates = sorted(order_dates[:NUM_POS])

    for i, order_date in enumerate(order_dates):
        po_id = f"PO{2023 + (i // 200):04d}{(i % 1000) + 1:03d}"
        # Ensure unique PO IDs
        po_id = f"PO{i+1:06d}"
        supplier_id = random.choice(supplier_ids)
        category = supplier_categories[supplier_id]
        material = random.choice(MATERIALS[category])
        quantity = round(random.uniform(50, 5000), 0)

        # Base prices vary by category
        base_prices = {
            "Raw Materials": random.uniform(150, 800),
            "Packaging": random.uniform(20, 200),
            "Electronics": random.uniform(50, 500),
            "Logistics": random.uniform(5000, 25000),
            "MRO": random.uniform(100, 1000),
        }
        base_price = base_prices[category]

        # Apply price drift for Raw Materials
        if category == "Raw Materials":
            unit_price = get_raw_material_price(base_price, order_date)
        else:
            unit_price = round(base_price * random.uniform(0.92, 1.08), 2)

        total_value = round(quantity * unit_price, 2)

        # Expected lead time: 7-30 days depending on category
        base_lead_days = {
            "Raw Materials": random.randint(10, 20),
            "Packaging": random.randint(5, 12),
            "Electronics": random.randint(14, 28),
            "Logistics": random.randint(3, 10),
            "MRO": random.randint(7, 15),
        }
        expected_lead = base_lead_days[category]
        expected_delivery = order_date + timedelta(days=expected_lead)

        # Determine delivery status based on supplier behavior
        behavior = get_supplier_behavior(supplier_id, order_date)

        # Recent POs are pending (after Jan 2026)
        if order_date > datetime(2026, 1, 15):
            status = "Pending"
            actual_delivery = None
        elif random.random() < 0.03:  # 3% cancellation rate
            status = "Cancelled"
            actual_delivery = None
        elif random.random() < behavior["delay_prob"]:
            status = "Delayed"
            delay = random.randint(*behavior["delay_days_range"])
            actual_delivery = expected_delivery + timedelta(days=delay)
        else:
            status = "Delivered"
            # Some early deliveries
            # Keep lead time strictly positive (no same-day delivery artifacts)
            early_cap = min(3, max(expected_lead - 1, 0))
            early = random.randint(0, early_cap)
            actual_delivery = expected_delivery - timedelta(days=early)

        purchase_orders.append({
            "po_id": po_id,
            "supplier_id": supplier_id,
            "material_name": material,
            "category": category,
            "quantity": quantity,
            "unit": "units" if category != "Logistics" else "trips",
            "unit_price": unit_price,
            "total_value": total_value,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "expected_delivery": expected_delivery.strftime("%Y-%m-%d"),
            "actual_delivery": actual_delivery.strftime("%Y-%m-%d") if actual_delivery else None,
            "status": status,
        })

    return pd.DataFrame(purchase_orders)


# ============================================================
# Generate Goods Receipts
# ============================================================
def generate_goods_receipts(po_df, suppliers_df):
    """Generate one goods receipt per delivered/delayed PO."""
    receipts = []
    delivered_pos = po_df[po_df["status"].isin(["Delivered", "Delayed"])].copy()

    for idx, (_, po) in enumerate(delivered_pos.iterrows()):
        receipt_id = f"GR{idx+1:06d}"
        received_date = po["actual_delivery"]

        # Fulfillment ratio — most are full, some are partial
        behavior = get_supplier_behavior(po["supplier_id"])
        if po["supplier_id"] in BAD_SUPPLIERS and random.random() < 0.25:
            # Bad suppliers sometimes short-ship
            received_qty = round(po["quantity"] * random.uniform(0.65, 0.90), 0)
            condition = "Partial"
        elif random.random() < 0.05:
            # Random partial delivery
            received_qty = round(po["quantity"] * random.uniform(0.80, 0.95), 0)
            condition = "Partial"
        else:
            received_qty = po["quantity"]
            condition = "Accepted"

        # Very rarely fully rejected
        if po["supplier_id"] in BAD_SUPPLIERS and random.random() < 0.08:
            condition = "Rejected"

        receipts.append({
            "receipt_id": receipt_id,
            "po_id": po["po_id"],
            "received_date": received_date,
            "received_quantity": received_qty,
            "condition": condition,
            "warehouse_location": random.choice(WAREHOUSES),
            "received_by": fake.name(),
        })

    return pd.DataFrame(receipts)


# ============================================================
# Generate Quality Inspections
# ============================================================
def generate_quality_inspections(receipts_df, po_df, suppliers_df):
    """Generate one quality inspection per goods receipt."""
    inspections = []
    po_supplier_map = dict(zip(po_df["po_id"], po_df["supplier_id"]))
    po_date_map = dict(zip(po_df["po_id"], po_df["order_date"]))

    for idx, (_, receipt) in enumerate(receipts_df.iterrows()):
        inspection_id = f"QI{idx+1:06d}"
        supplier_id = po_supplier_map[receipt["po_id"]]
        order_date_str = po_date_map[receipt["po_id"]]
        order_date = datetime.strptime(order_date_str, "%Y-%m-%d") if isinstance(order_date_str, str) else order_date_str

        behavior = get_supplier_behavior(supplier_id, order_date)

        # Generate defect rate based on supplier behavior
        defect_rate = round(np.clip(
            random.uniform(*behavior["defect_rate_range"]),
            0.0, 100.0
        ), 2)

        # Determine inspection result
        if defect_rate > 10.0:
            result = "Fail"
        elif defect_rate > 5.0:
            result = "Conditional"
        else:
            result = "Pass"

        # Inspection date is 1-3 days after receipt
        recv_date = datetime.strptime(receipt["received_date"], "%Y-%m-%d") if isinstance(receipt["received_date"], str) else receipt["received_date"]
        inspection_date = recv_date + timedelta(days=random.randint(1, 3))

        defect_type = random.choice(DEFECT_TYPES) if defect_rate > 2.0 else None

        remarks = None
        if result == "Fail":
            remarks = random.choice([
                "Batch rejected due to high defect rate.",
                "Quality below acceptable standards. Return to supplier.",
                "Critical defects found. Full batch inspection required.",
                "Non-conformance report raised. Supplier notified.",
            ])
        elif result == "Conditional":
            remarks = random.choice([
                "Accepted with minor deviations. Supplier warned.",
                "Partial rework needed before use.",
                "Accepted for non-critical applications only.",
            ])

        inspections.append({
            "inspection_id": inspection_id,
            "receipt_id": receipt["receipt_id"],
            "inspection_date": inspection_date.strftime("%Y-%m-%d"),
            "inspector_name": random.choice(INSPECTORS),
            "defect_rate_pct": defect_rate,
            "defect_type": defect_type,
            "inspection_result": result,
            "remarks": remarks,
        })

    return pd.DataFrame(inspections)


# ============================================================
# Generate Communications
# ============================================================
def generate_communications(suppliers_df):
    """Generate 420+ communication records."""
    communications = []
    supplier_ids = suppliers_df["supplier_id"].tolist()

    for i in range(NUM_COMMUNICATIONS):
        comm_id = f"CM{i+1:06d}"
        supplier_id = random.choice(supplier_ids)
        comm_date = random_date(datetime(2023, 1, 1), datetime(2026, 3, 31))
        behavior = get_supplier_behavior(supplier_id, comm_date)

        channel = random.choices(
            CHANNELS,
            weights=[0.45, 0.25, 0.15, 0.15],  # Email dominant
            k=1
        )[0]

        subject = random.choice(COMM_SUBJECTS)
        priority = random.choices(PRIORITIES, weights=[0.15, 0.50, 0.25, 0.10], k=1)[0]

        # Response time and resolution based on supplier behavior
        if random.random() < 0.85:  # 85% resolved
            response_time = round(
                random.uniform(*behavior["response_time_range"]) * random.uniform(0.5, 1.5),
                1
            )
            resolved = "Yes"
        else:
            response_time = None
            resolved = "No"

        # Bad suppliers have more unresolved communications
        if supplier_id in BAD_SUPPLIERS and random.random() < 0.25:
            resolved = "No"
            response_time = None

        communications.append({
            "comm_id": comm_id,
            "supplier_id": supplier_id,
            "comm_date": comm_date.strftime("%Y-%m-%d"),
            "channel": channel,
            "subject": subject,
            "priority": priority,
            "response_time_hours": response_time,
            "resolved": resolved,
        })

    return pd.DataFrame(communications)


# ============================================================
# Generate Contracts
# ============================================================
def generate_contracts(suppliers_df):
    """Generate 30 contracts (one per supplier) with specific expiry patterns."""
    contracts = []

    for idx, (_, supplier) in enumerate(suppliers_df.iterrows()):
        contract_id = f"CT{idx+1:06d}"
        supplier_id = supplier["supplier_id"]

        # Determine contract dates
        # 3 contracts expiring within 30 days of April 2026
        if supplier_id in ["SUP005", "SUP012", "SUP019"]:
            # Expiring between April 10-30, 2026
            end_date = datetime(2026, 4, random.randint(10, 30))
            start_date = end_date - timedelta(days=random.randint(365, 365 * 2))
            renewal_status = "Under Review"
        elif supplier_id in BAD_SUPPLIERS:
            # Some expired
            end_date = random_date(datetime(2025, 6, 1), datetime(2025, 12, 31))
            start_date = end_date - timedelta(days=random.randint(365, 365 * 3))
            renewal_status = "Expired"
        elif random.random() < 0.2:
            # Renewed contracts
            start_date = random_date(datetime(2022, 1, 1), datetime(2023, 6, 1))
            end_date = random_date(datetime(2026, 6, 1), datetime(2027, 12, 31))
            renewal_status = "Renewed"
        else:
            # Active contracts
            start_date = random_date(datetime(2022, 1, 1), datetime(2024, 1, 1))
            end_date = random_date(datetime(2026, 6, 1), datetime(2028, 12, 31))
            renewal_status = "Active"

        value_inr = round(random.uniform(500000, 50000000), 2)  # 5L to 5Cr INR
        sla_lead_time = random.randint(7, 25)
        sla_defect_limit = round(random.uniform(2.0, 8.0), 1)

        penalty_clauses = [
            "2% penalty per day of delay beyond SLA lead time",
            "5% deduction for defect rate exceeding SLA limit",
            "Contract review triggered after 3 consecutive SLA breaches",
            "10% rebate on next order for quality failures",
            "Supplier bears return shipping for rejected batches",
        ]

        contracts.append({
            "contract_id": contract_id,
            "supplier_id": supplier_id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "value_inr": value_inr,
            "sla_lead_time_days": sla_lead_time,
            "sla_defect_limit_pct": sla_defect_limit,
            "penalty_clause": random.choice(penalty_clauses),
            "renewal_status": renewal_status,
        })

    return pd.DataFrame(contracts)


# ============================================================
# Save to SQLite
# ============================================================
def save_to_sqlite(suppliers_df, po_df, receipts_df, inspections_df, comms_df, contracts_df, db_path):
    """Create SQLite database and populate all tables."""
    # Remove existing DB
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    # Insert data (exclude computed columns)
    suppliers_df.to_sql("Suppliers", conn, if_exists="replace", index=False)

    # For PurchaseOrders, we need to insert without the delay_days column (it's VIRTUAL)
    po_cols = [c for c in po_df.columns if c != "delay_days"]
    po_df[po_cols].to_sql("PurchaseOrders", conn, if_exists="replace", index=False)

    receipts_df.to_sql("GoodsReceipts", conn, if_exists="replace", index=False)
    inspections_df.to_sql("QualityInspections", conn, if_exists="replace", index=False)
    comms_df.to_sql("Communications", conn, if_exists="replace", index=False)
    contracts_df.to_sql("Contracts", conn, if_exists="replace", index=False)

    conn.commit()

    # Verify counts
    print("\n=== Database Population Summary ===")
    for table in ["Suppliers", "PurchaseOrders", "GoodsReceipts",
                   "QualityInspections", "Communications", "Contracts"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")

    conn.close()
    print(f"\nDatabase saved to: {db_path}")


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("SCME P6 - Generating Synthetic Data")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Step 1: Generate Suppliers
    print("\n[1/6] Generating Suppliers...")
    suppliers_df = generate_suppliers()
    print(f"  -> {len(suppliers_df)} suppliers generated")

    # Step 2: Generate Purchase Orders
    print("[2/6] Generating Purchase Orders...")
    po_df = generate_purchase_orders(suppliers_df)
    print(f"  -> {len(po_df)} purchase orders generated")
    print(f"  -> Status breakdown: {po_df['status'].value_counts().to_dict()}")

    # Verify seasonal spike
    po_df_temp = po_df.copy()
    po_df_temp["month"] = pd.to_datetime(po_df_temp["order_date"]).dt.month
    q3_count = po_df_temp[po_df_temp["month"].isin([7, 8, 9])].shape[0]
    other_q_avg = po_df_temp[~po_df_temp["month"].isin([7, 8, 9])].shape[0] / 3
    print(f"  -> Q3 POs: {q3_count}, Avg other quarter POs: {other_q_avg:.0f} (Q3 spike ratio: {q3_count/max(other_q_avg,1):.1f}x)")

    # Step 3: Generate Goods Receipts
    print("[3/6] Generating Goods Receipts...")
    receipts_df = generate_goods_receipts(po_df, suppliers_df)
    print(f"  -> {len(receipts_df)} goods receipts generated")

    # Step 4: Generate Quality Inspections
    print("[4/6] Generating Quality Inspections...")
    inspections_df = generate_quality_inspections(receipts_df, po_df, suppliers_df)
    print(f"  -> {len(inspections_df)} inspections generated")
    print(f"  -> Results: {inspections_df['inspection_result'].value_counts().to_dict()}")

    # Step 5: Generate Communications
    print("[5/6] Generating Communications...")
    comms_df = generate_communications(suppliers_df)
    print(f"  -> {len(comms_df)} communications generated")

    # Step 6: Generate Contracts
    print("[6/6] Generating Contracts...")
    contracts_df = generate_contracts(suppliers_df)
    print(f"  -> {len(contracts_df)} contracts generated")
    print(f"  -> Renewal status: {contracts_df['renewal_status'].value_counts().to_dict()}")

    # Save CSVs
    print("\nSaving CSV files...")
    csv_files = {
        "suppliers.csv": suppliers_df,
        "purchase_orders.csv": po_df,
        "goods_receipts.csv": receipts_df,
        "quality_inspections.csv": inspections_df,
        "communications.csv": comms_df,
        "contracts.csv": contracts_df,
    }
    for filename, df in csv_files.items():
        filepath = os.path.join(base_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"  -> {filename} ({len(df)} rows)")

    # Save to SQLite
    print("\nCreating SQLite database...")
    db_path = os.path.join(base_dir, "scm_p6.db")
    save_to_sqlite(suppliers_df, po_df, receipts_df, inspections_df, comms_df, contracts_df, db_path)

    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
