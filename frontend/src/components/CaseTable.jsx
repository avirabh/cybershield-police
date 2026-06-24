import React from "react";
import { Link } from "react-router-dom";
import { ExternalLink } from "lucide-react";
import { RiskBadge } from "./RiskBadge.jsx";
import { TriagePriority } from "./TriagePriority.jsx";

export default function CaseTable({ cases = [], emptyMessage = "No cases available yet. Analyze a demo message to create one." }) {
  if (!cases.length) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="table-wrap">
      <table className="case-table">
        <thead>
          <tr>
            <th>Case</th>
            <th>Category</th>
            <th>Platform</th>
            <th>Risk</th>
            <th>Police Priority</th>
            <th>Created</th>
            <th aria-label="Open case" />
          </tr>
        </thead>
        <tbody>
          {cases.map((item) => {
            const message = item.message || "No message text stored.";
            return (
              <tr key={item.id}>
                <td>
                  <strong>#{item.id}</strong>
                  <span>{message.slice(0, 78)}{message.length > 78 ? "..." : ""}</span>
                </td>
                <td>{item.category}</td>
                <td>{item.platform || "Unknown"}</td>
                <td>
                  <div className="risk-cell">
                    <RiskBadge level={item.risk_level} />
                    <span>{item.risk_score}</span>
                  </div>
                </td>
                <td>
                  <TriagePriority
                    priority={item.police_triage_priority}
                    explanation={item.police_triage_explanation}
                    compact
                  />
                </td>
                <td>{new Date(`${item.created_at}Z`).toLocaleString()}</td>
                <td>
                  <Link className="icon-link" to={`/cases/${item.id}`} aria-label={`Open case ${item.id}`}>
                    <ExternalLink size={17} />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
