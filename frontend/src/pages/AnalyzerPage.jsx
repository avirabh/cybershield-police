import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  BadgeIndianRupee,
  ClipboardCheck,
  FileText,
  Link2,
  MessageSquareText,
  SearchCheck,
  Send,
  ShieldCheck,
} from "lucide-react";
import { api } from "../api.js";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";

const initialForm = {
  message: "",
  url: "",
  platform: "SMS",
  victim_age_group: "Adult",
  amount_involved: "",
};

const demoMessage =
  "FAKE DEMO: Your bank KYC expires today. Verify PAN and Aadhaar now or account will be blocked. Login at kyc-bank-update.demo.test";

function formatMode(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function collectMatchedPatterns(result) {
  const fromTopLevel = result?.matched_patterns?.map((match) => match.pattern).filter(Boolean) || [];
  const fromFactors =
    result?.risk_factors?.flatMap((factor) => factor.matched_patterns || []).filter(Boolean) || [];
  return Array.from(new Set([...fromTopLevel, ...fromFactors])).slice(0, 10);
}

export default function AnalyzerPage() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = {
        ...form,
        amount_involved: form.amount_involved === "" ? null : Number(form.amount_involved),
      };
      const analysis = await api.analyze(payload);
      setResult(analysis);
    } catch (err) {
      setError(err.message || "Unable to analyze this report.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Citizen + Police Intake</span>
        <h1>Scam Analyzer</h1>
        <p>Paste a suspicious SMS, WhatsApp message, email, or URL to generate an explainable risk assessment.</p>
      </div>

      <div className="analyzer-layout">
        <form className="panel analyzer-form" onSubmit={submit}>
          <label>
            <span>
              <MessageSquareText size={17} />
              Suspicious message
            </span>
            <textarea
              name="message"
              rows="8"
              value={form.message}
              onChange={updateField}
              placeholder="Paste suspicious SMS, WhatsApp, or email text here"
            />
          </label>

          <label>
            <span>
              <Link2 size={17} />
              Suspicious URL
            </span>
            <input
              name="url"
              value={form.url}
              onChange={updateField}
              placeholder="https://example-link.test"
              type="text"
            />
          </label>

          <div className="form-grid">
            <label>
              <span>Platform</span>
              <select name="platform" value={form.platform} onChange={updateField}>
                <option>SMS</option>
                <option>WhatsApp</option>
                <option>Email</option>
                <option>Telegram</option>
                <option>Phone Call Note</option>
                <option>Social Media</option>
                <option>Other</option>
              </select>
            </label>

            <label>
              <span>Victim age group</span>
              <select name="victim_age_group" value={form.victim_age_group} onChange={updateField}>
                <option>Adult</option>
                <option>Student</option>
                <option>Senior Citizen</option>
                <option>Teen</option>
                <option>Unknown</option>
              </select>
            </label>

            <label>
              <span>
                <BadgeIndianRupee size={16} />
                Amount involved
              </span>
              <input
                name="amount_involved"
                value={form.amount_involved}
                onChange={updateField}
                placeholder="0"
                min="0"
                step="1"
                type="number"
              />
            </label>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="button button-secondary"
              onClick={() => setForm({ ...initialForm, message: demoMessage, url: "https://kyc-bank-update.demo.test/login" })}
            >
              <FileText size={18} />
              Load Demo
            </button>
            <button className="button button-primary" type="submit" disabled={loading}>
              <Send size={18} />
              {loading ? "Analyzing" : "Analyze"}
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}
        </form>

        <aside className="panel result-panel">
          {!result ? (
            <div className="result-placeholder">
              <SearchCheck size={36} />
              <h2>Risk result appears here</h2>
              <p>Submit a message, call note, or URL to view risk score, matched evidence, explanations, and police triage.</p>
            </div>
          ) : (
            <>
              <div className="result-header">
                <div>
                  <span className="eyebrow">Case #{result.id}</span>
                  <h2>{result.category}</h2>
                </div>
                <Link className="button button-ghost compact" to={`/cases/${result.id}`}>
                  <ClipboardCheck size={16} />
                  View Case
                </Link>
              </div>

              <RiskMeter score={result.risk_score} level={result.risk_level} />
              <TriagePriority
                priority={result.police_triage_priority}
                explanation={result.police_triage_explanation}
              />

              <div className="confidence-grid">
                <div className="confidence-card">
                  <span>Confidence</span>
                  <strong>{result.confidence_score ?? 0}%</strong>
                </div>
                <div className="confidence-card">
                  <span>Detected Categories</span>
                  <div className="category-stack">
                    {(result.categories?.length ? result.categories : [{ name: result.category }]).map((category) => (
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
                  <strong className="compact-strong">{formatMode(result.detection_mode)}</strong>
                </div>
                <div className="confidence-card">
                  <span>Signals Used</span>
                  <div className="category-stack">
                    {(result.signal_sources?.length ? result.signal_sources : ["none"]).map((source) => (
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
                  <h3>Matched Scam Patterns</h3>
                </div>
                {collectMatchedPatterns(result).length ? (
                  <div className="pattern-chip-list">
                    {collectMatchedPatterns(result).map((pattern) => (
                      <span key={pattern}>{pattern}</span>
                    ))}
                  </div>
                ) : (
                  <p>No strong pattern matches were found.</p>
                )}
              </div>

              <div className="evidence-grid">
                <div className="insight-card citizen-card">
                  <h3>Citizen Explanation</h3>
                  <p>{result.citizen_explanation}</p>
                </div>
                <div className="insight-card police-card">
                  <h3>Police Investigation Summary</h3>
                  <p>{result.police_summary}</p>
                </div>
                <div className="insight-card action-card">
                  <h3>Recommended Citizen Action</h3>
                  <p>{result.recommended_citizen_action || result.recommended_action}</p>
                </div>
                <div className="insight-card action-card">
                  <h3>Recommended Police Action</h3>
                  <p>{result.recommended_police_action}</p>
                </div>
              </div>

              <div className="factors-list">
                <h3>Triggered Risk Factors</h3>
                {result.risk_factors.length ? (
                  result.risk_factors.map((factor) => (
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
            </>
          )}
        </aside>
      </div>
    </section>
  );
}
