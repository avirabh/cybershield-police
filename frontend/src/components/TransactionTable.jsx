import React from "react";
import { RiskBadge } from "./RiskBadge.jsx";
import { TriagePriority } from "./TriagePriority.jsx";

function formatAmount(value) {
  return `Rs. ${Number(value || 0).toLocaleString("en-IN")}`;
}

export default function TransactionTable({
  transactions = [],
  emptyMessage = "No monitored transactions available yet.",
}) {
  if (!transactions.length) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="table-wrap">
      <table className="case-table transaction-table">
        <thead>
          <tr>
            <th>Transaction</th>
            <th>Amount</th>
            <th>Method</th>
            <th>Fraud Type</th>
            <th>Risk</th>
            <th>Police Priority</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>{item.transaction_id || `#${item.id}`}</strong>
                <span>{item.merchant_or_receiver_name || "Unknown receiver"}</span>
              </td>
              <td>{formatAmount(item.amount)}</td>
              <td>{item.payment_method || "Unknown"}</td>
              <td>{item.suspected_fraud_type}</td>
              <td>
                <div className="risk-cell">
                  <RiskBadge level={item.risk_level} />
                  <span>{item.risk_score}</span>
                </div>
              </td>
              <td>
                <TriagePriority priority={item.police_triage_priority} compact />
              </td>
              <td>{item.timestamp || item.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
