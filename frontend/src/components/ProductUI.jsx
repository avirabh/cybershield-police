import React from "react";
import { AlertTriangle, ClipboardList, ShieldCheck } from "lucide-react";

const statusClass = {
  New: "status-new",
  "Under Review": "status-under-review",
  "Verified Scam": "status-verified-scam",
  Escalated: "status-escalated",
  Closed: "status-closed",
  "Closed - Awareness Given": "status-closed",
  "Evidence Requested": "status-evidence-requested",
};

export function PageHeader({ eyebrow, title, subtitle, action }) {
  return (
    <div className="page-heading page-heading-enhanced">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action && <div className="page-header-action">{action}</div>}
    </div>
  );
}

export function SectionCard({ title, subtitle, children, className = "" }) {
  return (
    <section className={`panel section-card ${className}`}>
      {(title || subtitle) && (
        <div className="panel-heading">
          <h2>{title}</h2>
          {subtitle && <span>{subtitle}</span>}
        </div>
      )}
      {children}
    </section>
  );
}

export function StatCard({ label, value, icon: Icon = ClipboardList, tone = "blue", helper }) {
  return (
    <article className={`stat-card command-stat-card stat-${tone}`}>
      <Icon size={24} />
      <span>{label}</span>
      <strong>{value}</strong>
      {helper && <small>{helper}</small>}
    </article>
  );
}

export function StatusBadge({ status }) {
  const value = status || "New";
  return <span className={`status-pill ${statusClass[value] || "status-new"}`}>{value}</span>;
}

export function AlertCard({ title, children, tone = "warning", icon: Icon = AlertTriangle }) {
  return (
    <div className={`alert-card alert-card-${tone}`}>
      <Icon size={20} />
      <div>
        <strong>{title}</strong>
        <p>{children}</p>
      </div>
    </div>
  );
}

export function EmptyState({ icon: Icon = ShieldCheck, title = "No data yet", children }) {
  return (
    <div className="empty-state-card">
      <Icon size={34} />
      <strong>{title}</strong>
      {children && <p>{children}</p>}
    </div>
  );
}

export function CaseSummaryCard({ report }) {
  return (
    <article className="case-summary-card">
      <div>
        <span className="eyebrow">{report.tracking_id || `Case #${report.id}`}</span>
        <h3>{report.detected_category || report.category || "Unknown Suspicious"}</h3>
        <p>{report.police_summary || report.description || "Synthetic case summary pending review."}</p>
      </div>
      <dl>
        <div><dt>Location</dt><dd>{report.location || "Not provided"}</dd></div>
        <div><dt>Status</dt><dd><StatusBadge status={report.status} /></dd></div>
        <div><dt>Amount</dt><dd>Rs. {Number(report.transaction_amount || report.amount_involved || 0).toLocaleString("en-IN")}</dd></div>
      </dl>
    </article>
  );
}
