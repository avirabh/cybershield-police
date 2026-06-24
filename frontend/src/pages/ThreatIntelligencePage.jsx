import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Radar, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";

export default function ThreatIntelligencePage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getThreatIntel().then(setData).catch((err) => setError(err.message || "Unable to load threat intelligence."));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <LoadingState label="Loading CTI feed" />;

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Cyber Threat Intelligence</span>
        <h1>CTI Dashboard</h1>
        <p>{data.weekly_trend_insight}</p>
      </div>
      <div className="stats-grid">
        <article className="stat-card"><Radar size={24} /><span>Incidents</span><strong>{data.total_incidents}</strong></article>
        <article className="stat-card"><ShieldAlert size={24} /><span>High-Risk Indicators</span><strong>{data.high_risk_indicators_count}</strong></article>
        <article className="stat-card"><Radar size={24} /><span>Active Clusters</span><strong>{data.active_clusters_count}</strong></article>
      </div>
      <section className="panel">
        <div className="panel-heading"><h2>Simulated Alerts</h2><span>Fictional trend cards</span></div>
        <div className="cluster-mini-grid">
          {data.trend_cards.map((card) => <div className="cluster-mini-card" key={card.title}><strong>{card.title}</strong><span>{card.value}</span><p>{card.detail}</p></div>)}
        </div>
      </section>
      <section className="panel">
        <div className="panel-heading"><h2>High-Risk Indicators</h2><Link to="/indicator-lookup">Search indicators</Link></div>
        <div className="table-wrap">
          <table className="case-table"><thead><tr><th>Type</th><th>Value</th><th>Risk</th><th>Priority</th></tr></thead><tbody>
            {data.high_risk_indicators.map((indicator) => <tr key={indicator.indicator_id}><td>{indicator.indicator_type}</td><td>{indicator.value}</td><td>{indicator.risk_score}</td><td>{indicator.police_triage_priority}</td></tr>)}
          </tbody></table>
        </div>
      </section>
    </section>
  );
}
