import React, { useEffect, useState } from "react";
import { CheckCircle2, FilePlus2, Link2, RotateCcw, Send } from "lucide-react";
import { api } from "../api.js";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { AlertCard } from "../components/ProductUI.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const emptyForm = { url: "", email_content: "", message: "", use_optional_ai: true };
const demoForm = {
  url: "https://cisce-result-verify.demo.test/login",
  email_content: "FAKE DEMO: CISCE certificate download is blocked. Enter OTP and pay Rs 499 verification fee to release marksheet urgently.",
  message: "",
  use_optional_ai: true,
};

function riskFactorLabel(item) {
  if (typeof item === "string") return item;
  return item?.label || item?.code || "Risk factor";
}

export default function PhishingScannerPage() {
  const { t } = useLanguage();
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [savedReport, setSavedReport] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);

  useEffect(() => {
    api.getAiStatus()
      .then((status) => {
        setAiStatus(status);
        setForm((current) => ({ ...current, use_optional_ai: Boolean(status.ai_enabled) }));
      })
      .catch(() => setAiStatus(null));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setSavedReport(null);
      setResult(await api.scanPhishing(form));
    } catch (err) {
      setError(err.message || "Unable to scan.");
    } finally {
      setLoading(false);
    }
  }

  function clearScanner() {
    setForm(emptyForm);
    setResult(null);
    setSavedReport(null);
    setError("");
  }

  async function saveAsReport() {
    if (!result) return;
    setSaving(true);
    setError("");
    try {
      const report = await api.submitReport({
        reporter_name: "Scanner Demo User",
        anonymous: false,
        age_group: "Unknown",
        contact_placeholder: "scanner-demo-contact",
        location: "Ongole",
        category: result.category,
        description: "Saved from URL/UPI Scam Validator for police triage.",
        suspicious_message: form.email_content || form.message,
        suspicious_url: form.url,
        transaction_amount: 0,
        payment_mode: "Not Applicable",
        receiver_placeholder: "",
        evidence_metadata: [
          { type: "source", value: "Saved from phishing scanner" },
          { type: "trusted_domain_status", value: result.trusted_domain_check?.status || "No URL" },
        ],
      });
      setSavedReport(report);
    } catch (err) {
      setError(err.message || "Unable to save scanner result as report.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">{t("scanner.eyebrow")}</span>
        <h1>{t("scanner.title")}</h1>
        <p>{t("scanner.subtitle")}</p>
      </div>
      <div className="analyzer-layout">
        <form className="panel analyzer-form" onSubmit={submit}>
          <label>
            <span><Link2 size={17} /> {t("scanner.url")}</span>
            <input
              value={form.url}
              onChange={(event) => setForm((current) => ({ ...current, url: event.target.value }))}
              placeholder={t("scanner.placeholderUrl")}
            />
          </label>
          <label>
            <span>{t("scanner.content")}</span>
            <textarea
              rows="8"
              value={form.email_content}
              onChange={(event) => setForm((current) => ({ ...current, email_content: event.target.value }))}
              placeholder={t("scanner.placeholderContent")}
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.use_optional_ai}
              onChange={(event) => setForm((current) => ({ ...current, use_optional_ai: event.target.checked }))}
            />
            <span>
              Use optional AI explanation when available. Current mode: {aiStatus?.active_provider_label || "Local"}.
              Avoid sensitive personal information.
            </span>
          </label>
          <div className="form-actions">
            <button className="button button-secondary" type="button" onClick={() => { setForm(demoForm); setResult(null); setError(""); }}>
              <Link2 size={18} />
              {t("scanner.loadDemo")}
            </button>
            <button className="button button-ghost" type="button" onClick={clearScanner}>
              <RotateCcw size={18} />
              {t("common.clear")}
            </button>
            <button className="button button-primary" type="submit" disabled={loading}>
              <Send size={18} />
              {loading ? t("scanner.scanning") : t("scanner.scan")}
            </button>
          </div>
          {error && <div className="error-banner">{error}</div>}
        </form>
        <aside className="panel result-panel">
          {!result ? <p className="empty-state">{t("scanner.empty")}</p> : (
            <>
              <h2>{result.category}</h2>
              <RiskMeter score={result.risk_score ?? result.phishing_risk_score} level={result.risk_level} />
              <div className="confidence-grid">
                <div className="confidence-card">
                  <span>{t("scanner.confidence")}</span>
                  <strong>{result.confidence ?? 0}%</strong>
                </div>
                <div className="confidence-card">
                  <span>{t("scanner.trustedDomain")}</span>
                  <strong className="compact-strong">{result.trusted_domain_check?.status || "No URL"}</strong>
                </div>
                <div className="confidence-card">
                  <span>URL reputation</span>
                  <strong className="compact-strong">{result.url_reputation?.label || "Local rules only"}</strong>
                </div>
              </div>
              <div className="insight-block">
                <h3>{t("scanner.domainAnalysis")}</h3>
                <p>{result.domain_analysis.domain} - {result.domain_analysis.trusted_domain_handling}</p>
                <p>{result.url_reputation?.explanation || result.domain_analysis.url_reputation_handling}</p>
              </div>
              <div className="insight-block">
                <h3>{result.ai_enhanced ? "AI Enhanced Explanation" : "Local Explanation"}</h3>
                <span className={`provider-badge ${result.ai_enhanced ? "is-ai" : "is-local"}`}>
                  {result.provider_used || (result.ai_enhanced ? "AI Provider" : "Local Fallback")}
                </span>
                <p>{result.ai_enhanced ? result.ai_explanation : result.local_explanation || result.explanation}</p>
              </div>
              <div className="insight-block">
                <h3>Local risk factors</h3>
                <div className="factor-list">
                  {(result.risk_factors?.length ? result.risk_factors : result.warnings || []).map((item) => {
                    const label = riskFactorLabel(item);
                    return <span className="category-chip" key={label}>{label}</span>;
                  })}
                </div>
              </div>
              <div className="insight-block"><h3>{t("scanner.policeSummary")}</h3><p>{result.police_summary}</p></div>
              <div className="insight-block"><h3>{t("scanner.recommendedAction")}</h3><p>{result.recommended_action}</p></div>
              <div className="form-actions">
                <button className="button button-secondary" type="button" onClick={saveAsReport} disabled={saving}>
                  <FilePlus2 size={18} />
                  {saving ? "Saving" : "Save as Police Report"}
                </button>
              </div>
              {savedReport && (
                <AlertCard title="Saved to police triage" tone="success" icon={CheckCircle2}>
                  Tracking ID {savedReport.tracking_id} is now available in Case Management and Police Dashboard.
                </AlertCard>
              )}
            </>
          )}
        </aside>
      </div>
    </section>
  );
}

