import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, Bot, CheckCircle2, RotateCcw, Send, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import LanguageSelector from "../components/LanguageSelector.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const quickPromptKeys = [
  { key: "check", text: "Is this a scam? FAKE DEMO: Your KYC will be blocked today. Share OTP and open this link now." },
  { key: "report", text: "How do I report cyber fraud in this app?" },
  { key: "otpShared", text: "I shared OTP with a caller. What should I do now?" },
  { key: "moneyPaid", text: "I paid money in a UPI fraud. What should I do first?" },
  { key: "arrest", text: "Someone says I am under digital arrest and must pay now. What should I do?" },
  { key: "upi", text: "Someone says I must enter UPI PIN to receive a refund. Is that safe?" },
  { key: "phishing", text: "How can I identify a phishing link?" },
  { key: "fakeJob", text: "A work-from-home job is asking for registration fee. Is it safe?" },
  { key: "investment", text: "A trading group promises guaranteed daily profit. Is this risky?" },
  { key: "call1930", text: "Money was lost in cyber fraud. How does 1930 help?" },
];

const contextPatterns = {
  paidMoney: /(paid money|money lost|amount debited|sent money|transferred|payment done|upi pin entered|డబ్బు పంపాను|पैसे भेजे|টাকা পাঠিয়েছি)/i,
  sharedOtp: /(shared otp|gave otp|entered otp|told otp|shared pin|password shared|cvv shared|ఓటీపీ ఇచ్చాను|ओटीपी बताया|ওটিপি দিয়েছি)/i,
  wantsReport: /(report|complaint|1930|cybercrime|fir|రిపోర్ట్|शिकायत|অভিযোগ)/i,
};

const templateIntentMap = {
  digital_arrest: "arrest",
  otp_shared: "otpShared",
  money_paid: "moneyPaid",
  upi_fraud: "upi",
  phishing_link: "phishing",
  fake_kyc: "fakeKyc",
  fake_job: "fakeJob",
  fake_loan: "fakeLoan",
  investment_scam: "investment",
  fake_customer_care: "customerCare",
  qr_code: "upi",
  report_guidance: "report",
  safety_refusal: "unsafe",
};

const providerLabels = {
  gemini: "Gemini",
  huggingface: "Hugging Face",
  openrouter: "OpenRouter",
  groq: "Groq",
  local_fallback: "Local",
};

export default function ChatbotPage() {
  const { language, t } = useLanguage();
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([
    {
      role: "assistant",
      text: t("chatbot.intro"),
      note: t("chatbot.prototypeNote"),
    },
  ]);
  const [chatContext, setChatContext] = useState({
    lastScamType: "",
    paidMoney: false,
    sharedOtp: false,
    wantsReport: false,
  });
  const [loading, setLoading] = useState(false);
  const [emergencyGuidance, setEmergencyGuidance] = useState("");
  const [aiStatus, setAiStatus] = useState(null);

  const quickPrompts = useMemo(
    () => quickPromptKeys.map((prompt) => ({ ...prompt, label: t(`chatbot.quick.${prompt.key}`) })),
    [t],
  );

  useEffect(() => {
    api.getAiStatus().then(setAiStatus).catch(() => setAiStatus(null));
  }, []);

  useEffect(() => {
    setConversation((current) => {
      if (current.length === 1 && current[0].role === "assistant") {
        return [{ role: "assistant", text: t("chatbot.intro"), note: t("chatbot.prototypeNote") }];
      }
      return current;
    });
  }, [language, t]);

  function updateContext(input, response = {}) {
    setChatContext((current) => ({
      lastScamType: response.analysis?.category || response.category || current.lastScamType,
      paidMoney: current.paidMoney || contextPatterns.paidMoney.test(input) || response.detected_intent === "money_paid",
      sharedOtp: current.sharedOtp || contextPatterns.sharedOtp.test(input) || response.detected_intent === "otp_shared",
      wantsReport: current.wantsReport || contextPatterns.wantsReport.test(input) || response.suggest_report,
    }));
  }

  function localizedAssistantText(input, response) {
    if (response.message) return response.message;
    if (response.reply) return response.reply;
    const templateKey = templateIntentMap[response.detected_intent] || templateIntentMap[response.intent];
    if (templateKey) return t(`chatbot.templates.${templateKey}`);
    if (response.analysis?.risk_score >= 51) return t("chatbot.templates.likelyScam");
    if (response.analysis?.risk_score <= 25) return t("chatbot.templates.likelySafe");
    if (!input.trim()) return t("chatbot.templates.unclear");
    return response.reply || t("chatbot.templates.unclear");
  }

  function buildAssistantItem(input, response) {
    const actions = [];
    if (response.suggest_report || response.detected_intent === "money_paid" || response.detected_intent === "otp_shared") {
      actions.push({ to: "/report-incident", label: t("chatbot.actions.reportIncident") });
    }
    if (response.detected_intent === "upi_fraud" || response.detected_intent === "money_paid") {
      actions.push({ to: "/transactions", label: t("chatbot.actions.openTransaction") });
    }
    actions.push({ to: "/phishing-scanner", label: t("chatbot.actions.openScanner") });
    actions.push({ to: "/screenshot-analyzer", label: "Scan screenshot" });

    return {
      role: "assistant",
      text: localizedAssistantText(input, response),
      backendText: "",
      analysis: response.analysis,
      intent: response.detected_intent || response.intent,
      providerUsed: response.provider_used || providerLabels[response.ai_provider] || "Local",
      aiMode: response.ai_mode || "local_rule_based",
      aiEnhanced: Boolean(response.ai_enhanced),
      actions,
      note: response.prototype_notice || t("chatbot.prototypeNote"),
    };
  }

  async function submit(event) {
    event.preventDefault();
    if (!message.trim()) return;
    const userMessage = message;
    setMessage("");
    setConversation((current) => [...current, { role: "user", text: userMessage }]);
    setLoading(true);
    try {
      const response = await api.chatbotMessage({
        message: userMessage,
        language,
        context: chatContext,
        use_optional_ai: aiStatus?.ai_enabled ?? true,
      });
      updateContext(userMessage, response);
      setConversation((current) => [...current, buildAssistantItem(userMessage, response)]);
      setEmergencyGuidance(t("chatbot.emergency") || response.emergency_guidance || "");
    } catch (err) {
      setConversation((current) => [
        ...current,
        { role: "assistant", text: err.message || t("chatbot.templates.unclear"), note: t("chatbot.prototypeNote") },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function usePrompt(text) {
    setMessage(text);
  }

  function resetChat() {
    setMessage("");
    setEmergencyGuidance("");
    setChatContext({ lastScamType: "", paidMoney: false, sharedOtp: false, wantsReport: false });
    setConversation([
      {
        role: "assistant",
        text: t("chatbot.resetText"),
        note: t("chatbot.prototypeNote"),
      },
    ]);
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div className="heading-with-control">
          <span className="eyebrow">{t("chatbot.eyebrow")}</span>
          <LanguageSelector compact />
        </div>
        <h1>{t("chatbot.title")}</h1>
        <p>{t("chatbot.subtitle")}</p>
      </div>
      <section className="panel chatbot-panel">
        <div className="chatbot-toolbar">
          <div className="quick-actions">
            {quickPrompts.map((prompt) => (
              <button className="quick-action" type="button" key={prompt.key} onClick={() => usePrompt(prompt.text)}>
                {prompt.label}
              </button>
            ))}
          </div>
          <button className="button button-ghost compact" type="button" onClick={resetChat}>
            <RotateCcw size={16} />
            {t("common.reset")}
          </button>
        </div>
        <div className="emergency-guidance">
          <ShieldAlert size={18} />
          <span>{emergencyGuidance || t("chatbot.emergency")}</span>
        </div>
        <div className="chat-window">
          {conversation.length === 0 ? (
            <div className="empty-state"><Bot size={32} />{t("chatbot.templates.unclear")}</div>
          ) : (
            conversation.map((item, index) => (
              <div className={`chat-message ${item.role}`} key={`${item.role}-${index}`}>
                <p>{item.text}</p>
                {item.providerUsed ? (
                  <span className={`provider-badge ${item.aiEnhanced ? "is-ai" : "is-local"}`}>
                    {item.aiEnhanced ? "AI Enhanced" : "Local Safety Mode"} - {item.providerUsed}
                  </span>
                ) : null}
                {item.analysis ? (
                  <div className="chat-analysis-card">
                    <div>
                      <span>{t("chatbot.labels.riskScore")}</span>
                      <strong>{item.analysis.risk_score}/100</strong>
                    </div>
                    <div>
                      <span>{t("chatbot.labels.category")}</span>
                      <strong>{item.analysis.category}</strong>
                    </div>
                    <div>
                      <span>{t("chatbot.labels.priority")}</span>
                      <strong>{item.analysis.police_triage_priority}</strong>
                    </div>
                  </div>
                ) : null}
                {item.backendText && item.analysis ? <small>{item.backendText}</small> : null}
                {item.actions?.length ? (
                  <div className="chat-action-row">
                    {item.actions.map((action) => (
                      <Link className="quick-action chat-link-action" to={action.to} key={action.to}>
                        {action.to === "/report-incident" ? <AlertTriangle size={14} /> : <CheckCircle2 size={14} />}
                        {action.label}
                      </Link>
                    ))}
                  </div>
                ) : null}
                {item.note ? <em>{item.note}</em> : null}
              </div>
            ))
          )}
          {loading && <div className="typing-indicator"><span /> <span /> <span /> {t("chatbot.checking")}</div>}
        </div>
        <form className="chat-form" onSubmit={submit}>
          <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder={t("chatbot.placeholder")} />
          <button className="button button-primary" type="submit"><Send size={18} /> {t("common.send")}</button>
        </form>
      </section>
    </section>
  );
}
