import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ClipboardCheck, FileText, Send } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskMeter, RiskBadge } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";
import { AlertCard, PageHeader, SectionCard, StatusBadge } from "../components/ProductUI.jsx";

export default function CaseManagementPage() {
  const { id } = useParams();
  const [reports, setReports] = useState(null);
  const [report, setReport] = useState(null);
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("Under Review");
  const [error, setError] = useState("");

  async function load() {
    try {
      if (id) setReport(await api.getReport(id));
      else setReports(await api.getReports());
    } catch (err) {
      setError(err.message || "Unable to load case management.");
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function updateStatus() {
    const updated = await api.updateReportStatus(id, { status, evidence_reviewed: true });
    setReport(updated);
  }

  async function assign() {
    const updated = await api.assignReport(id, "officer@example.com");
    setReport(updated);
  }

  async function addNote() {
    if (!note.trim()) return;
    const updated = await api.addReportNote(id, { officer_email: "officer@example.com", note });
    setReport(updated);
    setNote("");
  }

  if (error) return <div className="error-banner">{error}</div>;
  if (id && !report) return <LoadingState label="Loading report" />;
  if (!id && !reports) return <LoadingState label="Loading reports" />;

  if (!id) {
    return (
      <section className="page-stack">
        <PageHeader
          eyebrow="Police Case Management"
          title="Citizen Report Queue"
          subtitle="Open a report to assign an officer, review evidence metadata, update status, and prepare an investigation summary."
        />
        <section className="panel">
          <div className="table-wrap">
            <table className="case-table">
              <thead>
                <tr>
                  <th>Tracking ID</th>
                  <th>Category</th>
                  <th>Risk</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Officer</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((item) => (
                  <tr key={item.id}>
                    <td><Link to={`/case-management/${item.id}`}>{item.tracking_id}</Link></td>
                    <td>{item.detected_category}</td>
                    <td><RiskBadge level={item.risk_level} /></td>
                    <td>{item.police_triage_priority}</td>
                    <td><StatusBadge status={item.status} /></td>
                    <td>{item.assigned_officer || "Unassigned"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    );
  }

  const firDraft = [
    `Tracking ID: ${report.tracking_id}`,
    `Reported location: ${report.location || "Not provided"}`,
    `Detected category: ${report.detected_category}`,
    `Risk score: ${report.risk_score}/100 (${report.risk_level})`,
    `Submitted description: ${report.description || "No description submitted."}`,
    `Evidence summary: message/url/transaction placeholders reviewed in CyberShield Police demo.`,
  ].join("\n");
  const timeline = [
    { label: "Report submitted", detail: report.created_at ? new Date(`${report.created_at}Z`).toLocaleString() : "Demo timestamp" },
    { label: "Automated triage", detail: `${report.risk_level} risk, ${report.police_triage_priority}` },
    { label: "Evidence review", detail: report.evidence_reviewed ? "Evidence metadata reviewed" : "Evidence metadata pending review" },
    { label: "Current status", detail: report.status || "New" },
  ];

  return (
    <section className="page-stack">
      <PageHeader eyebrow={report.tracking_id} title="Case Management Detail" subtitle={report.police_summary} />
      <div className="case-management-grid">
        <section className="panel">
          <RiskMeter score={report.risk_score} level={report.risk_level} />
          <TriagePriority priority={report.police_triage_priority} explanation={report.police_summary} />
          <div className="detail-list">
            <div><span>Status</span><strong><StatusBadge status={report.status} /></strong></div>
            <div><span>Assigned Officer</span><strong>{report.assigned_officer || "Unassigned"}</strong></div>
            <div><span>Location</span><strong>{report.location || "Not provided"}</strong></div>
            <div><span>Amount</span><strong>Rs. {Number(report.transaction_amount || 0).toLocaleString("en-IN")}</strong></div>
          </div>
          <AlertCard title="1930 urgent guidance" tone="warning">
            If financial loss happened recently, preserve transaction IDs and guide the citizen to call/report through 1930 quickly.
          </AlertCard>
          <div className="form-actions">
            <button className="button button-secondary" type="button" onClick={assign}>
              <ClipboardCheck size={18} /> Assign Demo Officer
            </button>
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              <option>New</option>
              <option>Under Review</option>
              <option>Verified Scam</option>
              <option>Escalated</option>
              <option>Closed</option>
            </select>
            <button className="button button-primary" type="button" onClick={updateStatus}>Update Status</button>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Evidence & Notes</h2>
            <span>Fictional demo evidence only</span>
          </div>
          <div className="insight-block">
            <h3>Message</h3>
            <p>{report.suspicious_message || report.description || "No message submitted."}</p>
          </div>
          <div className="evidence-metadata-list">
            {(report.evidence_metadata || []).map((item, index) => (
              <div key={`${item.type || "evidence"}-${index}`}>
                <strong>{item.filename || item.type || "Evidence metadata"}</strong>
                <span>{item.size_label || item.value || item.file_type || "Demo placeholder"}</span>
              </div>
            ))}
          </div>
          <div className="note-list">
            {(report.notes || []).map((item) => (
              <div className="note-card" key={item.id}>
                <strong>{item.officer_email}</strong>
                <p>{item.note}</p>
              </div>
            ))}
          </div>
          <label>
            <span>Add officer note</span>
            <textarea rows="3" value={note} onChange={(event) => setNote(event.target.value)} />
          </label>
          <button className="button button-primary" type="button" onClick={addNote}>
            <Send size={18} /> Add Note
          </button>
        </section>
      </div>

      <div className="dashboard-grid">
        <SectionCard title="Case Timeline" subtitle="Demo investigation lifecycle">
          <div className="case-timeline">
            {timeline.map((item) => (
              <div key={item.label}>
                <span />
                <strong>{item.label}</strong>
                <p>{item.detail}</p>
              </div>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="Recommended Action" subtitle="Police triage guidance">
          <p>{report.recommended_police_action || report.recommended_action || "Review submitted evidence metadata and contact the citizen through verified channels."}</p>
        </SectionCard>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>Case Summary / FIR Draft Aid</h2>
          <span>Investigation writing support, not an official FIR</span>
        </div>
        <pre className="fir-box"><FileText size={18} />{firDraft}</pre>
      </section>
    </section>
  );
}
