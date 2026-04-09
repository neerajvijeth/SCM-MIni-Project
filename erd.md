# Entity-Relationship Diagram — SCME P6 Supplier Relationship Management

```mermaid
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

## Table Relationships

| Relationship | Type | Description |
|---|---|---|
| Suppliers → PurchaseOrders | One-to-Many | Each supplier can have multiple purchase orders |
| Suppliers → Communications | One-to-Many | All communication records are linked to a supplier |
| Suppliers → Contracts | One-to-Many | Each supplier is governed by one or more contracts |
| PurchaseOrders → GoodsReceipts | One-to-One | Each delivered PO has one corresponding receipt |
| GoodsReceipts → QualityInspections | One-to-One | Each receipt undergoes one quality inspection |
