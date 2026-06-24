import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  Banknote,
  BriefcaseBusiness,
  CalendarClock,
  FilePlus2,
  Gift,
  Landmark,
  Link2,
  MessageSquareWarning,
  PhoneCall,
  QrCode,
  ReceiptIndianRupee,
  Send,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  Upload,
} from "lucide-react";
import { api } from "../api.js";
import { getStoredUser } from "../auth.js";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";
import LanguageSelector from "../components/LanguageSelector.jsx";
import { AlertCard, EmptyState, PageHeader, SectionCard } from "../components/ProductUI.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const initialForm = {
  reporter_name: "Demo Citizen",
  anonymous: false,
  age_group: "Adult",
  contact_placeholder: "demo-contact-placeholder",
  location: "Ongole",
  category: "Suspicious Message",
  description: "",
  suspicious_message: "",
  suspicious_url: "",
  transaction_amount: "",
  payment_mode: "UPI",
  receiver_placeholder: "",
  incident_time: "",
};

const steps = [
  "Category",
  "Incident Details",
  "Evidence Metadata",
  "Review & Submit",
];

const mandals = [
  "Ongole",
  "Chirala",
  "Markapur",
  "Kandukur",
  "Giddalur",
  "Kanigiri",
  "Addanki",
  "Darsi",
  "Podili",
  "Yerragondapalem",
  "Cumbum",
  "Tangutur",
];

const categoryOptions = [
  { value: "Digital Arrest Threat", label: "Digital Arrest", icon: PhoneCall },
  { value: "Investment Scam", label: "Investment Scam", icon: ReceiptIndianRupee },
  { value: "Phishing", label: "Phishing", icon: Link2 },
  { value: "UPI Fraud", label: "UPI Fraud", icon: Smartphone },
  { value: "OTP Fraud", label: "OTP Fraud", icon: ShieldAlert },
  { value: "Fake KYC", label: "Fake KYC", icon: Landmark },
  { value: "Job Scam", label: "Fake Job", icon: BriefcaseBusiness },
  { value: "Loan Scam", label: "Fake Loan", icon: Banknote },
  { value: "Lottery Scam", label: "Lottery Scam", icon: Gift },
  { value: "Fake Customer Care", label: "Fake Customer Care", icon: MessageSquareWarning },
  { value: "QR Code Scam", label: "QR Code Scam", icon: QrCode },
  { value: "Suspicious Message", label: "Other / Suspicious", icon: FilePlus2 },
];

function formatBytes(size) {
  if (!size) return "0 KB";
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export default function IncidentReportPage() {
  const { language, t } = useLanguage();
  const user = getStoredUser();
  const [form, setForm] = useState({ ...initialForm, reporter_name: user?.name || initialForm.reporter_name });
  const [evidenceFiles, setEvidenceFiles] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedCategory = useMemo(
    () => categoryOptions.find((category) => category.value === form.category) || categoryOptions[0],
    [form.category],
  );
  const SelectedCategoryIcon = selectedCategory.icon;

  function updateField(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  function updateEvidence(event) {
    const files = Array.from(event.target.files || []).map((file) => ({
      filename: file.name,
      file_type: file.type || "unknown",
      size: file.size,
      upload_time: new Date().toISOString(),
    }));
    setEvidenceFiles(files);
  }

  function loadDemo() {
    setActiveStep(1);
    setEvidenceFiles([
      {
        filename: "demo-whatsapp-screenshot.png",
        file_type: "image/png",
        size: 184320,
        upload_time: new Date().toISOString(),
      },
    ]);
    setForm((current) => ({
      ...current,
      category: "Fake KYC",
      location: "Ongole",
      age_group: "Senior Citizen",
      description: "A caller claimed my bank account will be blocked today and pushed me to share OTP.",
      suspicious_message: "FAKE DEMO: Your KYC is pending. Share OTP and pay Rs 499 verification fee now or account will be blocked.",
      suspicious_url: "",
      transaction_amount: "499",
      payment_mode: "UPI",
      receiver_placeholder: "DEMO_RECEIVER_UPI_PLACEHOLDER",
      incident_time: new Date().toISOString().slice(0, 16),
    }));
  }

  async function submit(event) {
    event.preventDefault();
    if (activeStep < steps.length - 1) {
      setActiveStep((current) => current + 1);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    try {
      const evidence_metadata = [
        ...evidenceFiles.map((file) => ({ type: "file_metadata", ...file, size_label: formatBytes(file.size) })),
        { type: "incident_time", value: form.incident_time || "Not provided" },
        { type: "source", value: "Citizen submitted synthetic report" },
      ];
      const payload = {
        ...form,
        language_preference: language,
        transaction_amount: form.transaction_amount === "" ? 0 : Number(form.transaction_amount),
        evidence_metadata,
      };
      setResult(await api.submitReport(payload));
    } catch (err) {
      setError(err.message || "Unable to submit report.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow={t("report.eyebrow")}
        title={t("report.title")}
        subtitle="A guided cybercrime complaint workflow for synthetic demo reports, automated triage, and police-ready investigation summaries."
        action={<LanguageSelector compact />}
      />

      <AlertCard title="Privacy-safe demo workflow" tone="info" icon={ShieldCheck}>
        {t("common.safeData")} Evidence upload stores only filename, type, size, and upload time for demonstration.
      </AlertCard>

      <div className="report-progress" aria-label="Report progress">
        {steps.map((step, index) => (
          <button
            className={index === activeStep ? "active" : index < activeStep ? "complete" : ""}
            type="button"
            key={step}
            onClick={() => setActiveStep(index)}
          >
            <span>{index + 1}</span>
            {step}
          </button>
        ))}
      </div>

      <div className="analyzer-layout">
        <form className="panel analyzer-form report-workflow-form" onSubmit={submit}>
          {activeStep === 0 && (
            <>
              <div className="section-label">
                <h2>Select Incident Category</h2>
                <span>Internal backend values remain English for consistent analysis.</span>
              </div>
              <div className="category-picker-grid">
                {categoryOptions.map((category) => {
                  const Icon = category.icon;
                  return (
                    <button
                      className={form.category === category.value ? "category-picker active" : "category-picker"}
                      type="button"
                      key={category.value}
                      onClick={() => setForm((current) => ({ ...current, category: category.value }))}
                    >
                      <Icon size={22} />
                      <span>{category.label}</span>
                    </button>
                  );
                })}
              </div>
              <div className="form-grid two-column">
                <label>
                  <span>{t("report.reporterName")}</span>
                  <input name="reporter_name" value={form.reporter_name} onChange={updateField} />
                </label>
                <label>
                  <span>{t("report.ageGroup")}</span>
                  <select name="age_group" value={form.age_group} onChange={updateField}>
                    <option>Student</option>
                    <option>Adult</option>
                    <option>Senior Citizen</option>
                    <option>Business Owner</option>
                    <option>Job Seeker</option>
                  </select>
                </label>
                <label>
                  <span>Prakasam mandal / city</span>
                  <select name="location" value={form.location} onChange={updateField}>
                    {mandals.map((mandal) => <option key={mandal}>{mandal}</option>)}
                  </select>
                </label>
                <label className="checkbox-row report-checkbox">
                  <input name="anonymous" checked={form.anonymous} onChange={updateField} type="checkbox" />
                  <span>{t("report.anonymous")}</span>
                </label>
              </div>
            </>
          )}

          {activeStep === 1 && (
            <>
              <div className="section-label">
                <h2>Incident Details</h2>
                <span>Paste only fictional/demo content in this prototype.</span>
              </div>
              <label>
                <span>{t("report.description")}</span>
                <textarea name="description" rows="4" value={form.description} onChange={updateField} placeholder="Briefly explain what happened." />
              </label>
              <label>
                <span>{t("report.suspiciousMessage")}</span>
                <textarea name="suspicious_message" rows="6" value={form.suspicious_message} onChange={updateField} placeholder="Paste SMS, WhatsApp, email, Telegram, or call notes." />
              </label>
              <div className="form-grid two-column">
                <label>
                  <span>{t("report.suspiciousUrl")}</span>
                  <input name="suspicious_url" value={form.suspicious_url} onChange={updateField} placeholder="https://demo-link.example.test" />
                </label>
                <label>
                  <span>UPI/account placeholder</span>
                  <input name="receiver_placeholder" value={form.receiver_placeholder} onChange={updateField} placeholder="DEMO_RECEIVER_PLACEHOLDER" />
                </label>
                <label>
                  <span>{t("report.amount")}</span>
                  <input name="transaction_amount" value={form.transaction_amount} onChange={updateField} type="number" min="0" />
                </label>
                <label>
                  <span>{t("report.paymentMode")}</span>
                  <select name="payment_mode" value={form.payment_mode} onChange={updateField}>
                    <option>UPI</option>
                    <option>Bank Transfer</option>
                    <option>Wallet</option>
                    <option>Card</option>
                    <option>Not Applicable</option>
                  </select>
                </label>
                <label>
                  <span><CalendarClock size={17} /> Incident time</span>
                  <input name="incident_time" value={form.incident_time} onChange={updateField} type="datetime-local" />
                </label>
              </div>
            </>
          )}

          {activeStep === 2 && (
            <>
              <div className="section-label">
                <h2>Evidence Metadata</h2>
                <span>No real upload is performed; the demo stores safe metadata only.</span>
              </div>
              <label className="evidence-upload-box">
                <Upload size={28} />
                <strong>Attach demo evidence metadata</strong>
                <span>Screenshot, PDF, audio note, or message export placeholder</span>
                <input multiple onChange={updateEvidence} type="file" />
              </label>
              {evidenceFiles.length ? (
                <div className="evidence-metadata-list">
                  {evidenceFiles.map((file) => (
                    <div key={`${file.filename}-${file.size}`}>
                      <strong>{file.filename}</strong>
                      <span>{file.file_type || "unknown"} - {formatBytes(file.size)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="No evidence metadata selected">
                  You can still submit a report. Police will request more evidence if needed.
                </EmptyState>
              )}
            </>
          )}

          {activeStep === 3 && (
            <SectionCard title="Review Complaint" subtitle="This summary will be auto-classified and saved as a police triage case.">
              <div className="complaint-review-grid">
                <div><span>Category</span><strong>{selectedCategory.label}</strong></div>
                <div><span>Location</span><strong>{form.location}</strong></div>
                <div><span>Age group</span><strong>{form.age_group}</strong></div>
                <div><span>Amount</span><strong>Rs. {Number(form.transaction_amount || 0).toLocaleString("en-IN")}</strong></div>
                <div><span>Payment mode</span><strong>{form.payment_mode}</strong></div>
                <div><span>Evidence files</span><strong>{evidenceFiles.length}</strong></div>
              </div>
              <p className="message-box">{form.suspicious_message || form.description || "No message text added yet."}</p>
            </SectionCard>
          )}

          <div className="form-actions">
            <button className="button button-secondary" type="button" onClick={loadDemo}>
              <FilePlus2 size={18} />
              {t("report.loadDemo")}
            </button>
            {activeStep > 0 && (
              <button className="button button-ghost" type="button" onClick={() => setActiveStep((current) => current - 1)}>
                Back
              </button>
            )}
            <button className="button button-primary" type="submit" disabled={loading}>
              <Send size={18} />
              {activeStep < steps.length - 1 ? "Next" : loading ? t("report.submitting") : t("report.submit")}
            </button>
          </div>
          {error && <div className="error-banner"><AlertTriangle size={18} />{error}</div>}
        </form>

        <aside className="panel result-panel">
          {!result ? (
            <div className="result-placeholder">
              <SelectedCategoryIcon size={36} />
              <h2>Police triage will appear here</h2>
              <p>Submit the complaint to generate tracking ID, risk score, category, priority, and prevention guidance.</p>
            </div>
          ) : (
            <>
              <div className="result-header">
                <div>
                  <span className="eyebrow">{result.tracking_id}</span>
                  <h2>{result.detected_category}</h2>
                </div>
                <Link className="button button-ghost compact" to={`/case-management/${result.id}`}>{t("report.openCase")}</Link>
              </div>
              <RiskMeter score={result.risk_score} level={result.risk_level} />
              <TriagePriority priority={result.police_triage_priority} explanation={result.police_summary} />
              <AlertCard title="Urgent financial fraud guidance" tone="warning">
                If money was lost recently, preserve screenshots and transaction IDs, then call/report to 1930 immediately.
              </AlertCard>
              <div className="insight-block">
                <h3>{t("report.guidance")}</h3>
                <p>{result.citizen_explanation}</p>
              </div>
              <div className="insight-block">
                <h3>{t("report.recommended")}</h3>
                <p>{result.recommended_citizen_action}</p>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  );
}
