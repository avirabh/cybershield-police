import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, ShieldCheck, Trash2 } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";

function formatMode(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function collectMatchedPatterns(caseItem) {
  const fromTopLevel = caseItem?.matched_patterns?.map((match) => match.pattern).filter(Boolean) || [];
  const fromFactors =
    caseItem?.risk_factors?.flatMap((factor) => factor.matched_patterns || []).filter(Boolean) || [];
  return Array.from(new Set([...fromTopLevel, ...fromFactors])).slice(0, 12);
}

export default function CaseDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caseItem, setCaseItem] = useState(null);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    api
      .getCase(id)
      .then(setCaseItem)
      .catch((err) => setError(err.message || "Unable to load case."));
  }, [id]);

  async function deleteCurrentCase() {
    setDeleting(true);
    try {
      await api.deleteCase(id);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Unable to delete case.");
      setDeleting(false);
    }
  }

  if (error) {
    return (
      <section className="page-stack">
        <Link className="text-link" to="/dashboard">
          <ArrowLeft size={17} />
          Back to dashboard
        </Link>
        <div className="error-banner">{error}</div>
      </section>
    );
  }

  if (!caseItem) {
    return <LoadingState label="Loading case details" />;
  }

  const matchedPatterns = collectMatchedPatterns(caseItem);

  return (
    <section className="page-stack">
      <div className="case-toolbar">
        <Link className="text-link" to="/dashboard">
          <ArrowLeft size={17} />
          Back to dashboard
        </Link>
        <div className="toolbar-actions">
          <a className="button button-secondary" href={api.exportUrl(caseItem.id)}>
            <Download size={18} />
            Export PDF
          </a>
          <button className="button button-danger" type="button" onClick={deleteCurrentCase} disabled={deleting}>
            <Trash2 size={18} />
            {deleting ? "Deleting" : "Delete"}
          </button>
        </div>
      </div>

      <div className="case-detail-grid">
        <section className="panel case-main">
          <div className="page-heading compact-heading">
            <span className="eyebrow">Case #{caseItem.id}</span>
            <h1>{caseItem.category}</h1>
            <p>Created {new Date(`${caseItem.created_at}Z`).toLocaleString()}</p>
          </div>

          <RiskMeter score={caseItem.risk_score} level={caseItem.risk_level} />
          <TriagePriority
            priority={caseItem.police_triage_priority}
            explanation={caseItem.police_triage_explanation}
          />

          <div className="confidence-grid">
            <div className="confidence-card">
              <span>Confidence</span>
              <strong>{caseItem.confidence_score ?? 0}%</strong>
            </div>
            <div className="confidence-card">
              <span>Detected Categories</span>
              <div className="category-stack">
                {(caseItem.categories?.length ? caseItem.categories : [{ name: caseItem.category }]).map((category) => (
                  <span className="category-chip" key={category.name}>
                    {category.name}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="signal-grid">
            <div className="confidence-card">
              <span>Detection Mode</span>
              <strong className="compact-strong">{formatMode(caseItem.detection_mode)}</strong>
            </div>
            <div className="confidence-card">
              <span>Signals Used</span>
              <div className="category-stack">
                {(caseItem.signal_sources?.length ? caseItem.signal_sources : ["none"]).map((source) => (
                  <span className="category-chip" key={source}>
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="evidence-card">
            <div className="evidence-card-header">
              <ShieldCheck size={19} />
              <h2>Matched Scam Patterns</h2>
            </div>
            {matchedPatterns.length ? (
              <div className="pattern-chip-list">
                {matchedPatterns.map((pattern) => (
                  <span key={pattern}>{pattern}</span>
                ))}
              </div>
            ) : (
              <p>No strong pattern matches were found for this case.</p>
            )}
          </div>

          <div className="detail-section">
            <h2>Submitted Message</h2>
            <p className="message-box">{caseItem.message || "No message text submitted."}</p>
          </div>

          {caseItem.url && (
            <div className="detail-section">
              <h2>Submitted URL</h2>
              <p className="message-box">{caseItem.url}</p>
            </div>
          )}

          <div className="evidence-grid">
            <div className="insight-card citizen-card">
              <h2>Citizen Explanation</h2>
              <p>{caseItem.citizen_explanation}</p>
            </div>
            <div className="insight-card police-card">
              <h2>Police Investigation Summary</h2>
              <p>{caseItem.police_summary}</p>
            </div>
            <div className="insight-card action-card">
              <h2>Recommended Citizen Action</h2>
              <p>{caseItem.recommended_citizen_action || caseItem.recommended_action}</p>
            </div>
            <div className="insight-card action-card">
              <h2>Recommended Police Action</h2>
              <p>{caseItem.recommended_police_action}</p>
            </div>
          </div>
        </section>

        <aside className="panel case-side">
          <h2>Case Metadata</h2>
          <dl className="meta-list">
            <div>
              <dt>Platform</dt>
              <dd>{caseItem.platform || "Unknown"}</dd>
            </div>
            <div>
              <dt>Victim Age Group</dt>
              <dd>{caseItem.victim_age_group || "Not provided"}</dd>
            </div>
            <div>
              <dt>Amount Involved</dt>
              <dd>Rs. {Number(caseItem.amount_involved || 0).toLocaleString("en-IN")}</dd>
            </div>
          </dl>

          <h2>Risk Factors</h2>
          <div className="factors-list compact-factors">
            {caseItem.risk_factors?.length ? (
              caseItem.risk_factors.map((factor) => (
                <div className="factor-item" key={factor.code}>
                  <div>
                    <strong>{factor.label}</strong>
                    <p>{factor.evidence}</p>
                    {factor.matched_patterns?.length ? (
                      <p className="matched-patterns">Matched: {factor.matched_patterns.slice(0, 3).join(", ")}</p>
                    ) : null}
                  </div>
                  <span>+{factor.weight}</span>
                </div>
              ))
            ) : (
              <p>No strong risk factors detected.</p>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}
