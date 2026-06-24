import React, { useEffect, useState } from "react";
import { CheckCircle2, FileImage, FilePlus2, RotateCcw, Send, ShieldCheck } from "lucide-react";
import { api } from "../api.js";
import { AlertCard } from "../components/ProductUI.jsx";
import { RiskMeter } from "../components/RiskBadge.jsx";

const emptyForm = {
  filename: "",
  file_type: "",
  file_size: 0,
  upload_time: "",
  manual_text: "",
  url: "",
  use_optional_ai: false,
};

const demoText =
  "FAKE DEMO SCREENSHOT: Bank KYC expires today. Enter OTP and UPI PIN to unblock account. Open https://urgent-kyc-bank.demo.test/login and pay verification fee immediately.";

export default function ScreenshotAnalyzerPage() {
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [savedReport, setSavedReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getAiStatus().then(setAiStatus).catch(() => setAiStatus(null));
  }, []);

  function handleFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setForm((current) => ({
      ...current,
      filename: file.name,
      file_type: file.type,
      file_size: file.size,
      upload_time: new Date().toISOString(),
    }));
    setResult(null);
    setSavedReport(null);
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSavedReport(null);
    try {
      setResult(await api.analyzeScreenshot(form));
    } catch (err) {
      setError(err.message || "Unable to analyze screenshot metadata.");
    } finally {
      setLoading(false);
    }
  }

  function clearForm() {
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
        reporter_name: "Screenshot Analyzer Demo User",
        anonymous: false,
        age_group: "Unknown",
        contact_placeholder: "screenshot-demo-contact",
        location: "Ongole",
        category: result.category,
        description: "Saved from Screenshot Scam Analyzer for police triage.",
        suspicious_message: form.manual_text,
        suspicious_url: form.url,
        transaction_amount: 0,
        payment_mode: "Not Applicable",
        receiver_placeholder: "",
        evidence_metadata: [
          { type: "source", value: "Saved from screenshot analyzer" },
          { type: "filename", value: result.metadata.filename },
          { type: "file_type", value: result.metadata.file_type },
          { type: "stored_image_bytes", value: "false" },
        ],
      });
      setSavedReport(report);
    } catch (err) {
      setError(err.message || "Unable to save screenshot result as report.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Screenshot Scam Analyzer</span>
        <h1>Analyze scam screenshots safely</h1>
        <p>
          Upload image metadata and paste visible text from SMS, WhatsApp, fake KYC pages, job offers, loan offers,
          payment screens, or digital arrest messages. This prototype does not identify people or store image bytes.
        </p>
      </div>

      <div className="analyzer-layout">
        <form className="panel analyzer-form" onSubmit={submit}>
          <label className="evidence-upload-box">
            <FileImage size={22} />
            <strong>{form.filename || "Choose screenshot metadata"}</strong>
            <span>PNG, JPG, JPEG, or WEBP. Metadata only is sent for analysis.</span>
            <input type="file" accept=".png,.jpg,.jpeg,.webp,image/png,image/jpeg,image/webp" onChange={handleFile} />
          </label>

          <label>
            <span>Visible screenshot text</span>
            <textarea
              rows="8"
              value={form.manual_text}
              onChange={(event) => setForm((current) => ({ ...current, manual_text: event.target.value }))}
              placeholder="Paste text visible in the screenshot. Do not enter real OTP, PIN, password, CVV, bank details, or private evidence."
            />
          </label>

          <label>
            <span>Visible URL, if any</span>
            <input
              value={form.url}
              onChange={(event) => setForm((current) => ({ ...current, url: event.target.value }))}
              placeholder="https://example.demo.test/login"
            />
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.use_optional_ai}
              onChange={(event) => setForm((current) => ({ ...current, use_optional_ai: event.target.checked }))}
            />
            <span>Use optional AI analysis if configured. Avoid sensitive personal information.</span>
          </label>

          <div className="safe-note">
            <ShieldCheck size={17} />
            <span>
              AI status: {aiStatus?.active_provider || "local_fallback"}. External AI is disabled unless an API key is configured
              and this checkbox is selected.
            </span>
          </div>

          <div className="form-actions">
            <button
              className="button button-secondary"
              type="button"
              onClick={() => setForm((current) => ({ ...current, manual_text: demoText, url: "https://urgent-kyc-bank.demo.test/login" }))}
            >
              <FileImage size={18} />
              Load Demo
            </button>
            <button className="button button-ghost" type="button" onClick={clearForm}>
              <RotateCcw size={18} />
              Clear
            </button>
            <button className="button button-primary" type="submit" disabled={loading}>
              <Send size={18} />
              {loading ? "Analyzing" : "Analyze Screenshot"}
            </button>
          </div>
          {error && <div className="error-banner">{error}</div>}
        </form>

        <aside className="panel result-panel">
          {!result ? (
            <p className="empty-state">Screenshot risk results will appear here after you submit safe metadata and visible text.</p>
          ) : (
            <>
              <h2>{result.category}</h2>
              <RiskMeter score={result.risk_score} level={result.risk_level} />
              <div className="confidence-grid">
                <div className="confidence-card">
                  <span>Confidence</span>
                  <strong>{result.confidence_score}%</strong>
                </div>
                <div className="confidence-card">
                  <span>AI mode</span>
                  <strong className="compact-strong">{result.ai_provider}</strong>
                </div>
              </div>
              <div className="insight-block"><h3>Extracted Text Preview</h3><p>{result.extracted_text_preview}</p></div>
              <div className="factor-list">{result.image_risk_factors.map((item) => <span className="category-chip" key={item}>{item}</span>)}</div>
              <div className="insight-block"><h3>Citizen Explanation</h3><p>{result.citizen_explanation}</p></div>
              <div className="insight-block"><h3>AI / Local Explanation</h3><p>{result.ai_explanation}</p></div>
              <div className="insight-block"><h3>Police Summary</h3><p>{result.police_summary}</p></div>
              <div className="insight-block"><h3>Recommended Action</h3><p>{result.recommended_action}</p></div>
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
