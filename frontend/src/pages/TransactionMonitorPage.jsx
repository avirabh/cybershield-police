import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  BadgeIndianRupee,
  CheckCircle2,
  Clock,
  CreditCard,
  FilePlus2,
  MapPin,
  ReceiptText,
  RotateCcw,
  Send,
  ShieldCheck,
  UserRoundCheck,
} from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskMeter } from "../components/RiskBadge.jsx";
import { TriagePriority } from "../components/TriagePriority.jsx";
import TransactionTable from "../components/TransactionTable.jsx";
import { AlertCard } from "../components/ProductUI.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const initialForm = {
  transaction_id: "",
  amount: "",
  payment_method: "UPI",
  merchant_or_receiver_name: "",
  receiver_upi_or_account_placeholder: "",
  timestamp: "",
  location_or_city: "",
  transaction_note: "",
  user_age_group: "Adult",
  previous_transaction_count: "0",
  is_first_time_receiver: "yes",
  reported_by_user: "no",
};

const demoTransaction = {
  ...initialForm,
  transaction_id: "",
  amount: "2499",
  merchant_or_receiver_name: "Demo QR Refund Receiver",
  receiver_upi_or_account_placeholder: "QR_REFUND_PLACEHOLDER_001",
  transaction_note: "FAKE DEMO: scan QR and enter UPI PIN to receive urgent refund now. Approve request immediately.",
  user_age_group: "Senior Citizen",
  previous_transaction_count: "6",
  reported_by_user: "yes",
};

function formatAmount(value) {
  return `Rs. ${Number(value || 0).toLocaleString("en-IN")}`;
}

function collectMatchedPatterns(result) {
  return Array.from(
    new Set(result?.risk_factors?.flatMap((factor) => factor.matched_patterns || []).filter(Boolean) || []),
  ).slice(0, 10);
}

export default function TransactionMonitorPage() {
  const { t } = useLanguage();
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [recent, setRecent] = useState([]);
  const [savedReport, setSavedReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingRecent, setLoadingRecent] = useState(true);
  const [error, setError] = useState("");
  const [savingReport, setSavingReport] = useState(false);

  useEffect(() => {
    api
      .getTransactions()
      .then((items) => setRecent(items.slice(0, 8)))
      .catch(() => setRecent([]))
      .finally(() => setLoadingRecent(false));
  }, []);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setSavedReport(null);

    try {
      const payload = {
        ...form,
        transaction_id: form.transaction_id.trim() || `DEMO-TXN-${Date.now()}`,
        amount: Number(form.amount || 0),
        previous_transaction_count: Number(form.previous_transaction_count || 0),
        is_first_time_receiver: form.is_first_time_receiver === "yes",
        reported_by_user: form.reported_by_user === "yes",
      };
      const analysis = await api.analyzeTransaction(payload);
      setResult(analysis);
      setForm((current) => (current.transaction_id.trim() ? current : { ...current, transaction_id: payload.transaction_id }));
      setRecent((current) => [analysis, ...current.filter((item) => item.id !== analysis.id)].slice(0, 8));
    } catch (err) {
      setError(err.message || "Unable to analyze this transaction.");
    } finally {
      setLoading(false);
    }
  }

  const matchedPatterns = collectMatchedPatterns(result);

  function resetForm() {
    setForm(initialForm);
    setResult(null);
    setSavedReport(null);
    setError("");
  }

  async function saveAsReport() {
    if (!result) return;
    setSavingReport(true);
    setError("");
    try {
      const report = await api.submitReport({
        reporter_name: "Transaction Monitor Demo",
        anonymous: false,
        age_group: form.user_age_group || "Unknown",
        contact_placeholder: "transaction-monitor-demo",
        location: form.location_or_city || "Ongole",
        category: result.suspected_fraud_type,
        description: `Saved from Transaction Monitor. ${result.police_summary}`,
        suspicious_message: form.transaction_note,
        suspicious_url: "",
        transaction_amount: Number(result.amount || form.amount || 0),
        payment_mode: result.payment_method || form.payment_method,
        receiver_placeholder: form.receiver_upi_or_account_placeholder,
        evidence_metadata: [
          { type: "source", value: "Saved from transaction monitor" },
          { type: "transaction_id", value: result.transaction_id || form.transaction_id || `DEMO-TXN-${result.id}` },
          { type: "receiver_placeholder", value: form.receiver_upi_or_account_placeholder || "Not provided" },
        ],
      });
      setSavedReport(report);
    } catch (err) {
      setError(err.message || "Unable to save transaction as report.");
    } finally {
      setSavingReport(false);
    }
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">{t("transaction.eyebrow")}</span>
        <h1>{t("transaction.title")}</h1>
        <p>{t("transaction.subtitle")}</p>
      </div>

      <div className="transaction-layout">
        <form className="panel analyzer-form" onSubmit={submit}>
          <div className="form-grid two-column">
            <label>
              <span>
                <ReceiptText size={17} />
                {t("transaction.id")}
              </span>
              <input
                name="transaction_id"
                value={form.transaction_id}
                onChange={updateField}
                placeholder={t("transaction.optionalId")}
              />
            </label>

            <label>
              <span>
                <BadgeIndianRupee size={17} />
                {t("transaction.amount")}
              </span>
              <input name="amount" value={form.amount} onChange={updateField} min="0" step="1" type="number" />
            </label>
          </div>

          <div className="form-grid two-column">
            <label>
              <span>
                <CreditCard size={17} />
                {t("transaction.paymentMethod")}
              </span>
              <select name="payment_method" value={form.payment_method} onChange={updateField}>
                <option>UPI</option>
                <option>bank transfer</option>
                <option>wallet</option>
                <option>card</option>
              </select>
            </label>

            <label>
              <span>
                <Clock size={17} />
                {t("transaction.timestamp")}
              </span>
              <input name="timestamp" value={form.timestamp} onChange={updateField} type="datetime-local" />
            </label>
          </div>

          <label>
            <span>
              <UserRoundCheck size={17} />
              {t("transaction.receiver")}
            </span>
            <input
              name="merchant_or_receiver_name"
              value={form.merchant_or_receiver_name}
              onChange={updateField}
              placeholder={t("transaction.receiverNamePlaceholder")}
            />
          </label>

          <label>
            <span>{t("transaction.receiverPlaceholder")}</span>
            <input
              name="receiver_upi_or_account_placeholder"
              value={form.receiver_upi_or_account_placeholder}
              onChange={updateField}
              placeholder={t("transaction.receiverPlaceholderText")}
            />
          </label>

          <label>
            <span>
              <MapPin size={17} />
              {t("transaction.city")}
            </span>
            <input name="location_or_city" value={form.location_or_city} onChange={updateField} placeholder={t("transaction.cityPlaceholder")} />
          </label>

          <label>
            <span>{t("transaction.note")}</span>
            <textarea
              name="transaction_note"
              value={form.transaction_note}
              onChange={updateField}
              placeholder={t("transaction.notePlaceholder")}
              rows="5"
            />
          </label>

          <div className="form-grid two-column">
            <label>
              <span>{t("transaction.userAgeGroup")}</span>
              <select name="user_age_group" value={form.user_age_group} onChange={updateField}>
                <option>Adult</option>
                <option>Senior Citizen</option>
                <option>Student</option>
                <option>Job Seeker</option>
                <option>Business Owner</option>
                <option>Unknown</option>
              </select>
            </label>

            <label>
              <span>{t("transaction.previousCount")}</span>
              <input
                name="previous_transaction_count"
                value={form.previous_transaction_count}
                onChange={updateField}
                min="0"
                step="1"
                type="number"
              />
            </label>
          </div>

          <div className="form-grid two-column">
            <label>
              <span>{t("transaction.firstTimeReceiver")}</span>
              <select name="is_first_time_receiver" value={form.is_first_time_receiver} onChange={updateField}>
                <option value="yes">{t("common.yes")}</option>
                <option value="no">{t("common.no")}</option>
              </select>
            </label>

            <label>
              <span>{t("transaction.reportedByUser")}</span>
              <select name="reported_by_user" value={form.reported_by_user} onChange={updateField}>
                <option value="no">{t("common.no")}</option>
                <option value="yes">{t("common.yes")}</option>
              </select>
            </label>
          </div>

          <div className="form-actions">
            <button type="button" className="button button-secondary" onClick={() => setForm(demoTransaction)}>
              <ReceiptText size={18} />
              {t("transaction.loadDemo")}
            </button>
            <button type="button" className="button button-ghost" onClick={resetForm}>
              <RotateCcw size={18} />
              {t("common.clear")}
            </button>
            <button className="button button-primary" type="submit" disabled={loading}>
              <Send size={18} />
              {loading ? t("transaction.analyzing") : t("transaction.analyze")}
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
              <ShieldCheck size={36} />
              <h2>{t("transaction.emptyTitle")}</h2>
              <p>{t("transaction.emptyText")}</p>
            </div>
          ) : (
            <>
              <div className="result-header">
                <div>
                  <span className="eyebrow">Transaction #{result.id}</span>
                  <h2>{result.suspected_fraud_type}</h2>
                </div>
                <strong className="amount-pill">{formatAmount(result.amount)}</strong>
              </div>

              <RiskMeter score={result.risk_score} level={result.risk_level} />
              <TriagePriority priority={result.police_triage_priority} />

              <div className="confidence-grid">
                <div className="confidence-card">
                  <span>{t("transaction.paymentMethod")}</span>
                  <strong className="compact-strong">{result.payment_method}</strong>
                </div>
                <div className="confidence-card">
                  <span>{t("transaction.receiverShort")}</span>
                  <strong className="compact-strong">{result.merchant_or_receiver_name || "Unknown"}</strong>
                </div>
              </div>

              <div className="evidence-card">
                <div className="evidence-card-header">
                  <ShieldCheck size={19} />
                  <h3>{t("transaction.matchedPatterns")}</h3>
                </div>
                {matchedPatterns.length ? (
                  <div className="pattern-chip-list">
                    {matchedPatterns.map((pattern) => (
                      <span key={pattern}>{pattern}</span>
                    ))}
                  </div>
                ) : (
                  <p>{t("transaction.noPatterns")}</p>
                )}
              </div>

              <div className="evidence-grid">
                <div className="insight-card citizen-card">
                  <h3>{t("transaction.citizenExplanation")}</h3>
                  <p>{result.citizen_explanation}</p>
                </div>
                <div className="insight-card police-card">
                  <h3>{t("transaction.policeSummary")}</h3>
                  <p>{result.police_summary}</p>
                </div>
                <div className="insight-card action-card">
                  <h3>{t("transaction.recommendedAction")}</h3>
                  <p>{result.recommended_action}</p>
                </div>
              </div>

              <div className="form-actions">
                <button className="button button-secondary" type="button" onClick={saveAsReport} disabled={savingReport}>
                  <FilePlus2 size={18} />
                  {savingReport ? "Saving" : "Save as Police Report"}
                </button>
              </div>
              {savedReport && (
                <AlertCard title="Saved to police triage" tone="success" icon={CheckCircle2}>
                  Tracking ID {savedReport.tracking_id} is now visible in Case Management and Police Dashboard.
                </AlertCard>
              )}

              <div className="factors-list">
                <h3>{t("transaction.triggeredFactors")}</h3>
                {result.risk_factors.length ? (
                  result.risk_factors.map((factor) => (
                    <div className="factor-item" key={factor.code}>
                      <div>
                        <strong>{factor.label}</strong>
                        <p>{factor.evidence}</p>
                        {factor.matched_patterns?.length ? (
                          <p className="matched-patterns">{t("transaction.matched")}: {factor.matched_patterns.slice(0, 3).join(", ")}</p>
                        ) : null}
                      </div>
                      <span>+{factor.weight}</span>
                    </div>
                  ))
                ) : (
                  <p>{t("transaction.noFactors")}</p>
                )}
              </div>
            </>
          )}
        </aside>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>{t("transaction.recentTitle")}</h2>
          <span>{t("transaction.recentSub")}</span>
        </div>
        {loadingRecent ? (
          <LoadingState label={t("transaction.loadingRecords")} />
        ) : (
          <TransactionTable transactions={recent} />
        )}
      </section>
    </section>
  );
}
