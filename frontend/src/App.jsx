import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

function Card({ title, value, hint }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value">{value}</div>
      {hint ? <div className="card-hint">{hint}</div> : null}
    </div>
  );
}

function ProgressRow({ label, value, max = 100 }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className="progress-row">
      <div className="progress-label">{label}</div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="progress-value">{value.toFixed(1)}</div>
    </div>
  );
}

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);
  const [riskRows, setRiskRows] = useState([]);
  const [anomalyRows, setAnomalyRows] = useState([]);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    async function loadAll() {
      setLoading(true);
      setError("");
      try {
        const [summaryRes, riskRes, anomalyRes, metricsRes] = await Promise.all([
          fetch(`${API_BASE}/api/summary`),
          fetch(`${API_BASE}/api/risk-suppliers?limit=8`),
          fetch(`${API_BASE}/api/anomalies?limit=8`),
          fetch(`${API_BASE}/api/model-metrics`)
        ]);

        if (!summaryRes.ok || !riskRes.ok || !anomalyRes.ok || !metricsRes.ok) {
          throw new Error("Failed to load one or more API endpoints.");
        }

        setSummary(await summaryRes.json());
        setRiskRows(await riskRes.json());
        setAnomalyRows(await anomalyRes.json());
        setMetrics(await metricsRes.json());
      } catch (err) {
        setError(err.message || "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  const leadMetricText = useMemo(() => {
    if (!metrics) return "-";
    const m1 = metrics.model1_lead_time_forecasting;
    return `LR RMSE ${m1.rmse_lr.toFixed(2)} | RF RMSE ${m1.rmse_rf.toFixed(2)}`;
  }, [metrics]);

  return (
    <div className="page">
      <header className="header">
        <h1>SCM P6 - Supplier Relationship Dashboard</h1>
        <p>Simple React + FastAPI UI for demo use</p>
      </header>

      {loading && <div className="status">Loading dashboard data...</div>}
      {error && <div className="status error">Error: {error}</div>}

      {!loading && !error && summary ? (
        <>
          <section className="kpi-grid">
            <Card title="Active Suppliers" value={summary.active_suppliers} />
            <Card title="On-Time Delivery" value={`${summary.on_time_delivery_pct}%`} />
            <Card title="Avg Lead Time" value={`${summary.average_lead_time_days} days`} />
            <Card title="Open POs" value={summary.open_purchase_orders} />
            <Card title="Delayed Orders" value={summary.delayed_orders} />
            <Card title="Anomalies Flagged" value={summary.anomaly_count} />
          </section>

          <section className="panel">
            <h2>Risky Suppliers (Top by Risk Score)</h2>
            {riskRows.map((row) => (
              <ProgressRow key={row.supplier_id} label={`${row.supplier_id} - ${row.name}`} value={row.risk_score} />
            ))}
          </section>

          <section className="panel">
            <h2>ML Snapshot</h2>
            <div className="metric-row">Lead Time Models: {leadMetricText}</div>
            <div className="metric-row">
              Risk Model Accuracy:{" "}
              {metrics
                ? `${(metrics.model2_supplier_risk_classification.accuracy * 100).toFixed(2)}%`
                : "-"}
            </div>
            <div className="metric-row">
              Anomaly Rate:{" "}
              {metrics
                ? `${metrics.model3_anomaly_detection.anomaly_rate_pct.toFixed(2)}%`
                : "-"}
            </div>
          </section>

          <section className="table-wrap">
            <h2>Top Risk Suppliers</h2>
            <table>
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Category</th>
                  <th>Risk Score</th>
                  <th>On-Time %</th>
                  <th>Defect %</th>
                  <th>Predicted Label</th>
                </tr>
              </thead>
              <tbody>
                {riskRows.map((row) => (
                  <tr key={row.supplier_id}>
                    <td>{row.name}</td>
                    <td>{row.category}</td>
                    <td>{row.risk_score.toFixed(2)}</td>
                    <td>{row.on_time_rate.toFixed(2)}</td>
                    <td>{row.avg_defect_rate.toFixed(2)}</td>
                    <td>{row.predicted_label}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="table-wrap">
            <h2>Flagged Goods Receipt Anomalies</h2>
            <table>
              <thead>
                <tr>
                  <th>Receipt ID</th>
                  <th>Supplier</th>
                  <th>Date</th>
                  <th>Defect %</th>
                  <th>Delay Days</th>
                  <th>Anomaly Score</th>
                </tr>
              </thead>
              <tbody>
                {anomalyRows.map((row) => (
                  <tr key={row.receipt_id}>
                    <td>{row.receipt_id}</td>
                    <td>{row.supplier_name}</td>
                    <td>{row.received_date}</td>
                    <td>{row.defect_rate_pct.toFixed(2)}</td>
                    <td>{row.delivery_delay_days}</td>
                    <td>{row.anomaly_score.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      ) : null}
    </div>
  );
}

export default App;
