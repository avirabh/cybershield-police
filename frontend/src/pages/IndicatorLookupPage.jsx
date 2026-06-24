import React, { useEffect, useState } from "react";
import { AlertTriangle, Search, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";

const demoQueries = [
  "98XXXXXX21",
  "fraudster-demo@upi",
  "ACCT-DEMO-4821",
  "suspicious-demo-login.example",
  "203.0.113.24",
  "scan QR to receive refund",
];

export default function IndicatorLookupPage() {
  const [query, setQuery] = useState("fraudster-demo@upi");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSearch(nextQuery = query) {
    setLoading(true);
    setError("");
    try {
      const result = await api.searchIndicators(nextQuery);
      setData(result);
      setQuery(nextQuery);
    } catch (err) {
      setError(err.message || "Unable to search indicators.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runSearch("fraudster-demo@upi");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const primary = data?.primary_result;

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Synthetic Indicator Intelligence</span>
        <h1>Indicator Lookup</h1>
        <p>Search masked phones, demo UPI placeholders, account placeholders, fake domains, demo IPs, keywords, and receiver names.</p>
      </div>

      <section className="panel lookup-panel">
        <form
          className="lookup-form"
          onSubmit={(event) => {
            event.preventDefault();
            runSearch();
          }}
        >
          <label>
            <span>
              <Search size={17} />
              Indicator search
            </span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="98XXXXXX21 or fraudster-demo@upi" />
          </label>
          <button className="button button-primary" type="submit" disabled={loading}>
            <Search size={18} />
            Search
          </button>
        </form>
        <div className="sample-strip">
          {demoQueries.map((item) => (
            <button className="chip-button" type="button" key={item} onClick={() => runSearch(item)}>
              {item}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      {loading && !data ? (
        <LoadingState label="Searching indicators" />
      ) : primary ? (
        <div className="indicator-layout">
          <section className="panel result-panel">
            <div className="result-header">
              <div>
                <span className="eyebrow">{primary.indicator_type}</span>
                <h2>{primary.value}</h2>
              </div>
              <ShieldAlert size={28} />
            </div>
            <RiskMeter score={primary.risk_score} level={primary.risk_score >= 76 ? "Critical" : primary.risk_score >= 51 ? "High" : "Medium"} />
            <TriagePriority priority={primary.police_triage_priority} />
            <div className="confidence-grid">
              <div className="confidence-card">
                <span>Related Cases</span>
                <strong>{primary.related_case_count}</strong>
              </div>
              <div className="confidence-card">
                <span>First / Last Seen</span>
                <strong className="compact-strong">{primary.first_seen} to {primary.last_seen}</strong>
              </div>
            </div>
            <div className="evidence-card">
              <div className="evidence-card-header">
                <ShieldAlert size={19} />
                <h3>Intelligence Summary</h3>
              </div>
              <p>{primary.intelligence_summary}</p>
            </div>
            <div className="evidence-grid">
              <div className="insight-card police-card">
                <h3>Linked Scam Categories</h3>
                <div className="category-stack">
                  {primary.linked_scam_categories.map((item) => <span className="category-chip" key={item}>{item}</span>)}
                </div>
              </div>
              <div className="insight-card citizen-card">
                <h3>Related Locations</h3>
                <div className="category-stack">
                  {primary.related_locations.map((item) => <span className="category-chip" key={item}>{item}</span>)}
                </div>
              </div>
              <div className="insight-card action-card">
                <h3>Related Indicators</h3>
                <div className="category-stack">
                  {primary.related_indicators.map((item) => <span className="category-chip" key={item}>{item}</span>)}
                </div>
              </div>
            </div>
          </section>

          <aside className="panel">
            <div className="panel-heading">
              <h2>Future Integrations</h2>
              <span>Not connected in demo</span>
            </div>
            <div className="future-list">
              {data.future_integrations.map((item) => (
                <div key={item}>{item}</div>
              ))}
            </div>
          </aside>
        </div>
      ) : (
        <p className="empty-state">No synthetic indicator matched that query.</p>
      )}

      <section className="panel">
        <div className="panel-heading">
          <h2>Related Synthetic Indicators</h2>
          <span>{data?.count || 0} matches</span>
        </div>
        <div className="table-wrap">
          <table className="case-table">
            <thead>
              <tr>
                <th>Indicator</th>
                <th>Type</th>
                <th>Risk</th>
                <th>Cases</th>
                <th>Categories</th>
                <th>Locations</th>
              </tr>
            </thead>
            <tbody>
              {(data?.results || []).map((item) => (
                <tr key={item.indicator_id}>
                  <td>
                    <strong>{item.value}</strong>
                    <span>{item.indicator_id}</span>
                  </td>
                  <td>{item.indicator_type}</td>
                  <td>{item.risk_score}</td>
                  <td>{item.related_case_count}</td>
                  <td>{item.linked_scam_categories.join(", ")}</td>
                  <td>{item.related_locations.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
