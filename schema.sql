-- ============================================================
-- SCME P6 — Supplier Relationship Management
-- Database Schema (SQLite)
-- UE23CS342BA1 — Supply Chain Management for Engineers
-- PES University | Jan–May 2026
-- ============================================================

-- Enable foreign key enforcement (SQLite requires this per-connection)
PRAGMA foreign_keys = ON;

-- ============================================================
-- Table 1: Suppliers (master entity)
-- Central table holding all supplier information.
-- Each supplier has a unique ID, belongs to a category,
-- and has contract and contact information.
-- ============================================================
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

-- ============================================================
-- Table 2: Purchase Orders
-- Tracks all purchase orders placed with suppliers.
-- Links to Suppliers via supplier_id.
-- delay_days is a computed virtual column for analysis.
-- ============================================================
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

-- ============================================================
-- Table 3: Goods Receipts
-- Records the receipt of goods against a purchase order.
-- One receipt per delivered/delayed PO.
-- Links to PurchaseOrders via po_id.
-- ============================================================
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

-- ============================================================
-- Table 4: Quality Inspections
-- Records inspection outcomes for each goods receipt.
-- One inspection per goods receipt.
-- Links to GoodsReceipts via receipt_id.
-- ============================================================
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

-- ============================================================
-- Table 5: Communications
-- Tracks all communications with suppliers.
-- Includes channel, priority, response time, and resolution status.
-- Links to Suppliers via supplier_id.
-- ============================================================
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

-- ============================================================
-- Table 6: Contracts
-- Manages supplier contracts with SLA terms, penalty clauses,
-- and renewal status tracking.
-- Links to Suppliers via supplier_id.
-- ============================================================
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
