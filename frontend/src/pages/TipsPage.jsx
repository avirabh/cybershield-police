import React from "react";
import {
  BadgeAlert,
  BadgeCheck,
  Building2,
  CreditCard,
  KeyRound,
  Link2Off,
  MessageCircleWarning,
  Smartphone,
} from "lucide-react";

const tips = [
  {
    title: "Never share OTP, PIN, CVV, or passwords",
    body: "Banks, police, government offices, and payment apps do not ask for secret codes over calls or messages.",
    icon: KeyRound,
  },
  {
    title: "Verify KYC alerts from official channels",
    body: "Open the official banking app or website manually. Do not use links from unsolicited SMS or WhatsApp messages.",
    icon: Building2,
  },
  {
    title: "Do not scan QR codes to receive money",
    body: "QR scans and UPI PIN entry are used to send money, not receive refunds, rewards, or support payments.",
    icon: Smartphone,
  },
  {
    title: "Treat urgent threats as suspicious",
    body: "Fraudsters use account blocking, legal action, parcel seizure, or deadline pressure to reduce careful thinking.",
    icon: BadgeAlert,
  },
  {
    title: "Check links before clicking",
    body: "Shortened links, misspelled domains, and unknown domains with bank or reward words are strong warning signs.",
    icon: Link2Off,
  },
  {
    title: "Avoid advance fees for jobs, loans, or prizes",
    body: "Registration fees, processing fees, and prize release fees are common hooks in fake job, loan, and lottery scams.",
    icon: CreditCard,
  },
];

const responseSteps = [
  {
    title: "Pause",
    body: "Do not click, pay, share OTP, scan QR, or continue the call while under pressure.",
    icon: BadgeAlert,
  },
  {
    title: "Preserve",
    body: "Keep screenshots, sender IDs, transaction references, URLs, call times, and chat handles.",
    icon: MessageCircleWarning,
  },
  {
    title: "Verify",
    body: "Use only official app, website, branch, or helpline details typed manually by the citizen.",
    icon: BadgeCheck,
  },
];

export default function TipsPage() {
  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Citizen Awareness</span>
        <h1>Awareness & Safety Tips</h1>
        <p>Clear prevention guidance for citizens, volunteers, and police awareness sessions.</p>
      </div>

      <section className="safety-strip" aria-label="Immediate safety response">
        {responseSteps.map((step) => {
          const Icon = step.icon;
          return (
            <div className="safety-step" key={step.title}>
              <Icon size={22} />
              <div>
                <strong>{step.title}</strong>
                <p>{step.body}</p>
              </div>
            </div>
          );
        })}
      </section>

      <div className="tips-grid">
        {tips.map((tip) => {
          const Icon = tip.icon;
          return (
            <article className="tip-card" key={tip.title}>
              <Icon size={24} />
              <h2>{tip.title}</h2>
              <p>{tip.body}</p>
            </article>
          );
        })}
      </div>

      <section className="panel report-flow">
        <div>
          <MessageCircleWarning size={28} />
          <h2>When a scam is suspected</h2>
          <p>
            Stop communication, preserve screenshots and transaction IDs, contact the bank/payment app immediately
            for financial loss, and report through official cybercrime channels.
          </p>
        </div>
        <div>
          <BadgeCheck size={28} />
          <h2>For police triage</h2>
          <p>
            Record sender handles, phone numbers, URLs, payment identifiers, timestamps, and repeated message patterns
            before evidence disappears.
          </p>
        </div>
      </section>
    </section>
  );
}
