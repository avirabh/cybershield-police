import React, { useEffect, useState } from "react";
import { AlertTriangle, GitBranch, Network, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskMeter } from "../components/RiskBadge.jsx";

function amountLabel(value) {
  return `Rs. ${Number(value || 0).toLocaleString("en-IN")}`;
}

export default function CasePatternAnalyzerPage() {
  const [clusters, setClusters] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getThreatClusters()
      .then((items) => {
        setClusters(items);
        setSelected(items[0] || null);
      })
      .catch((err) => setError(err.message || "Unable to load case clusters."))
      .finally(() => setLoading(false));
  }, []);

  if (error) {
    return (
      <section className="page-stack">
        <div className="error-banner">
          <AlertTriangle size={18} />
          {error}
        </div>
      </section>
    );
  }

  if (loading) {
    return <LoadingState label="Loading case pattern analyzer" />;
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Linked Case Intelligence</span>
        <h1>Case Pattern Analyzer</h1>
        <p>Find synthetic links between complaints through shared receiver placeholders, fake UPI IDs, domains, scripts, and target groups.</p>
      </div>

      <div className="cluster-layout">
        <aside className="panel cluster-list">
          <div className="panel-heading">
            <h2>Active Clusters</h2>
            <span>{clusters.length} synthetic clusters</span>
          </div>
          {clusters.map((cluster) => (
            <button
              className={`cluster-button ${selected?.cluster_id === cluster.cluster_id ? "active" : ""}`}
              key={cluster.cluster_id}
              type="button"
              onClick={() => setSelected(cluster)}
            >
              <strong>{cluster.cluster_name}</strong>
              <span>{cluster.linked_case_count} linked cases · {amountLabel(cluster.total_amount_lost)}</span>
            </button>
          ))}
        </aside>

        {selected ? (
          <section className="panel result-panel">
            <div className="result-header">
              <div>
                <span className="eyebrow">{selected.cluster_id}</span>
                <h2>{selected.cluster_name}</h2>
              </div>
              <Network size={30} />
            </div>

            <RiskMeter score={selected.risk_score} level={selected.risk_score >= 76 ? "Critical" : selected.risk_score >= 51 ? "High" : "Medium"} />

            <div className="confidence-grid">
              <div className="confidence-card">
                <span>Linked Cases</span>
                <strong>{selected.linked_case_count}</strong>
              </div>
              <div className="confidence-card">
                <span>Total Synthetic Amount Lost</span>
                <strong className="compact-strong">{amountLabel(selected.total_amount_lost)}</strong>
              </div>
            </div>

            <div className="network-panel" aria-label="Synthetic case network graph">
              <div className="network-center">
                <ShieldAlert size={20} />
                <span>{selected.cluster_name}</span>
              </div>
              {selected.shared_indicators.slice(0, 5).map((indicator, index) => (
                <div className={`network-node node-${index + 1}`} key={indicator}>
                  {indicator}
                </div>
              ))}
            </div>

            <div className="evidence-grid">
              <div className="insight-card police-card">
                <h3>Suspected Fraud Pattern</h3>
                <p>{selected.suspected_fraud_pattern}</p>
              </div>
              <div className="insight-card citizen-card">
                <h3>Evidence Summary</h3>
                <p>{selected.evidence_summary}</p>
              </div>
              <div className="insight-card action-card">
                <h3>Recommended Police Action</h3>
                <p>{selected.recommended_police_action}</p>
              </div>
            </div>

            <div className="dashboard-grid">
              <div className="evidence-card">
                <div className="evidence-card-header">
                  <GitBranch size={19} />
                  <h3>Common Risk Factors</h3>
                </div>
                <div className="category-stack">
                  {selected.common_risk_factors.map((item) => <span className="category-chip" key={item}>{item}</span>)}
                </div>
              </div>
              <div className="evidence-card">
                <div className="evidence-card-header">
                  <GitBranch size={19} />
                  <h3>Shared Indicators</h3>
                </div>
                <div className="category-stack">
                  {selected.shared_indicators.map((item) => <span className="category-chip" key={item}>{item}</span>)}
                </div>
              </div>
            </div>

            <div className="table-wrap">
              <table className="case-table">
                <thead>
                  <tr>
                    <th>Linked Case</th>
                    <th>Cluster</th>
                    <th>Pattern</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.linked_cases.map((caseId) => (
                    <tr key={caseId}>
                      <td><strong>{caseId}</strong></td>
                      <td>{selected.cluster_name}</td>
                      <td>{selected.suspected_fraud_pattern}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : (
          <p className="empty-state">No synthetic clusters available.</p>
        )}
      </div>
    </section>
  );
}
