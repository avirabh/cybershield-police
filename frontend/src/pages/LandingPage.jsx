import { Link, useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { Activity, ArrowRight, Building2, CreditCard, Database, FileImage, FileSearch, Gauge, Landmark, Link2, LockKeyhole, LogIn, LogOut, Radar, ScrollText, ShieldAlert, ShieldCheck, UserPlus, UserRound, UserRoundCog } from "lucide-react";
import { api } from "../api.js";
import { clearAuth, getStoredUser, roleHome, saveAuth } from "../auth.js";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const demoFlowKeys = [
  "Paste suspicious message",
  "Analyze risk",
  "View explanation and police triage",
  "Save case",
  "View dashboard analytics",
  "Open case details/report",
];

const roleAccessCards = [
  {
    title: "Citizen Access",
    role: "Citizen",
    icon: UserRound,
    text: "For reporting cyber fraud, checking scam/phishing messages, monitoring transaction risk, and using Awareness plus CyberDost.",
    features: ["Report cyber fraud", "Scam/phishing checking", "Transaction risk checking", "Awareness and CyberDost"],
    loginTo: "/login?mode=login&role=Citizen",
    registerTo: "/login?mode=register&role=Citizen",
    loginLabel: "Login as Citizen",
    registerLabel: "Register Citizen",
  },
  {
    title: "Police Officer Access",
    role: "Police Officer",
    icon: Landmark,
    text: "For managing complaints, viewing assigned cases, updating status, and generating summaries or FIR-style drafts.",
    features: ["Manage complaints", "View assigned cases", "Update case status", "Generate summaries/FIR drafts"],
    loginTo: "/login?mode=login&role=Police%20Officer",
    registerTo: "/login?mode=register&role=Police%20Officer",
    loginLabel: "Login as Police",
    registerLabel: "Register Police",
  },
  {
    title: "Admin/SP Access",
    role: "Admin/SP",
    icon: Building2,
    text: "For district-level analytics, police verification requests, threat intelligence, hotspot review, and case overview.",
    features: ["District analytics", "Police verification requests", "Threat intelligence dashboard", "Hotspot and case overview"],
    loginTo: "/login?mode=login&role=Admin/SP",
    loginLabel: "Login as Admin/SP",
  },
];

const demoAccounts = [
  { role: "Citizen", title: "Citizen Demo", email: "citizen@example.com", password: "citizen123", button: "Try Citizen Demo" },
  { role: "Police Officer", title: "Police Officer Demo", email: "officer@example.com", password: "officer123", button: "Try Police Demo" },
  { role: "Admin/SP", title: "Admin/SP Demo", email: "admin@example.com", password: "admin123", button: "Try Admin/SP Demo" },
];

const moduleOverview = [
  { title: "Citizen Reporting", text: "Guided complaint workflow with tracking ID, evidence metadata, and 1930 guidance.", icon: FileSearch },
  { title: "URL/UPI Scam Validator", text: "Checks messages, links, and payment placeholders with trusted-domain safeguards.", icon: Link2 },
  { title: "Screenshot Scam Analyzer", text: "Analyzes safe image metadata and pasted visible text without face recognition or storing image bytes.", icon: FileImage },
  { title: "Transaction Anomaly Detection", text: "Scores suspicious payment patterns such as QR refunds, fake loan fees, and repeated transfers.", icon: CreditCard },
  { title: "Cyber Threat Intelligence", text: "Synthetic Prakasam/AP trend stream, indicators, clusters, and hotspot intelligence.", icon: Radar },
  { title: "Police Investigation Dashboard", text: "Prioritizes reports, shows summaries, evidence metadata, notes, status, and FIR draft support.", icon: ShieldAlert },
];

const policeNeeds = [
  "Plain text scams often have no URL, so police need message-first triage.",
  "High-volume complaints need explainable prioritization before manual review.",
  "Evidence metadata, notes, and status updates keep case handling consistent.",
  "Synthetic hotspot and CTI views help demonstrate district-level prevention planning.",
];

export default function LandingPage() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [user, setUser] = useState(getStoredUser());
  const [demoLoadingRole, setDemoLoadingRole] = useState("");
  const [demoError, setDemoError] = useState("");

  useEffect(() => {
    api.getAnalytics().then(setAnalytics).catch(() => setAnalytics(null));
  }, []);

  useEffect(() => {
    function syncAuth() {
      setUser(getStoredUser());
    }
    window.addEventListener("cybershield-auth", syncAuth);
    window.addEventListener("storage", syncAuth);
    return () => {
      window.removeEventListener("cybershield-auth", syncAuth);
      window.removeEventListener("storage", syncAuth);
    };
  }, []);

  async function continueDemo(account) {
    setDemoError("");
    setDemoLoadingRole(account.role);
    try {
      const payload = await api.login({ email: account.email, password: account.password });
      saveAuth(payload);
      setUser(payload.user);
      navigate(roleHome(payload.user.role));
    } catch (err) {
      setDemoError(err.message || "Demo login failed. Make sure the backend is running.");
    } finally {
      setDemoLoadingRole("");
    }
  }

  function logoutFromHome() {
    clearAuth();
    setUser(null);
  }

  const total = analytics?.total_reports ?? 10;
  const highRisk = analytics?.high_risk_reports ?? 0;
  const critical = analytics?.critical_reports ?? 0;
  const textOnly = analytics?.text_only_scam_count ?? 0;
  const amountAtRisk = analytics?.transaction_total_amount ?? analytics?.total_monitored_amount ?? 0;

  return (
    <section className="landing">
      <div className="hero-band">
        <span className="hero-glow hero-glow-a" aria-hidden="true" />
        <span className="hero-glow hero-glow-b" aria-hidden="true" />
        <span className="hero-scan-line" aria-hidden="true" />
        <div className="hero-data-particles" aria-hidden="true">
          {Array.from({ length: 12 }).map((_, index) => (
            <span key={index} className={`particle particle-${index + 1}`} />
          ))}
        </div>
        <div className="hero-copy">
          <span className="eyebrow">{t("home.eyebrow")}</span>
          <h1>{t("home.title")}</h1>
          <p>
            {t("home.subtitle")}
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" to="/analyzer">
              <FileSearch size={18} />
              {t("home.analyze")}
            </Link>
            <Link className="button button-secondary" to="/dashboard">
              <Activity size={18} />
              {t("home.dashboard")}
            </Link>
            <Link className="button button-ghost" to="/transactions">
              <CreditCard size={18} />
              {t("home.transactions")}
            </Link>
          </div>
          <div className="hero-proof" aria-label="Demo readiness indicators">
            <span>{t("home.proof1")}</span>
            <span>{t("home.proof2")}</span>
            <span>{t("home.proof3")}</span>
          </div>
        </div>

        <div className="ops-visual" aria-label="Cybercrime operations preview">
          <div className="ops-header">
            <span>{t("home.liveTriage")}</span>
            <strong>{t("home.localDemo")}</strong>
          </div>
          <div className="radar-field beacon-field">
            <div className="cyber-shield-visual" aria-hidden="true">
              <span className="shield-orbit orbit-one" />
              <span className="shield-orbit orbit-two" />
              <span className="shield-node node-one" />
              <span className="shield-node node-two" />
              <span className="shield-node node-three" />
              <span className="shield-outline">
                <LockKeyhole size={34} />
              </span>
              <span className="shield-scan" />
            </div>
            <div className="police-beacon" aria-hidden="true">
              <span className="beacon-glass beacon-blue" />
              <span className="beacon-core" />
              <span className="beacon-glass beacon-red" />
            </div>
            <div className="beacon-caption">
              <strong>{t("home.beacon")}</strong>
              <span>{t("home.beaconText")}</span>
            </div>
            <span className="signal signal-a" />
            <span className="signal signal-b" />
            <span className="signal signal-c" />
          </div>
          <div className="ops-grid">
            <div>
              <small>{t("home.totalReports")}</small>
              <strong>{total}</strong>
            </div>
            <div>
              <small>{t("home.highRisk")}</small>
              <strong>{highRisk}</strong>
            </div>
            <div>
              <small>{t("home.critical")}</small>
              <strong>{critical}</strong>
            </div>
          </div>
          <div className="ops-queue">
            <div>
              <Gauge size={18} />
              <span>{t("home.priorityQueue")}</span>
              <strong>{analytics?.high_priority_cases?.length ?? 0}</strong>
            </div>
            <div>
              <ScrollText size={18} />
              <span>{t("home.textOnlyCases")}</span>
              <strong>{textOnly}</strong>
            </div>
          </div>
        </div>
      </div>

      <section className="panel" aria-label="Practical social impact">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Practical Impact</span>
            <h2>Report to Analyze to Triage to Investigate to Warn Public</h2>
          </div>
          <span>All numbers are synthetic demo metrics for hackathon evaluation.</span>
        </div>
        <div className="role-action-grid">
          <article className="role-action-card">
            <ShieldAlert size={24} />
            <strong>{total} reports triaged</strong>
            <span>Citizens can check suspicious messages, links, screenshots, and transactions before harm spreads.</span>
          </article>
          <article className="role-action-card">
            <Gauge size={24} />
            <strong>{highRisk + critical} high-risk alerts</strong>
            <span>Police get explainable priority queues instead of manually scanning every complaint first.</span>
          </article>
          <article className="role-action-card">
            <CreditCard size={24} />
            <strong>Rs {Number(amountAtRisk || 0).toLocaleString("en-IN")} monitored</strong>
            <span>Transaction monitoring demonstrates how suspicious payment patterns can be surfaced safely.</span>
          </article>
        </div>
      </section>

      <section className="access-panel" aria-label="CyberShield Police login access">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Role-Based Access</span>
            <h2>Access CyberShield Police</h2>
          </div>
          <span>Authentication is mock/demo-based for hackathon evaluation.</span>
        </div>
        <div className="role-access-grid">
          {roleAccessCards.map((card) => {
            const Icon = card.icon;
            return (
              <article className={`role-access-card role-${card.role.toLowerCase().replaceAll("/", "-").replaceAll(" ", "-")}`} key={card.role}>
                <div className="role-access-icon"><Icon size={25} /></div>
                <span className="role-badge">{card.role}</span>
                <h3>{card.title}</h3>
                <p>{card.text}</p>
                <ul>
                  {card.features.map((feature) => <li key={feature}>{feature}</li>)}
                </ul>
                <div className="role-access-actions">
                  <Link className="button button-primary compact" to={card.loginTo}>
                    <LogIn size={16} />
                    {card.loginLabel}
                  </Link>
                  {card.registerTo && (
                    <Link className="button button-ghost compact" to={card.registerTo}>
                      <UserPlus size={16} />
                      {card.registerLabel}
                    </Link>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {user ? (
        <section className="panel home-account-panel" aria-label="Current account overview">
          <div className="account-overview-main">
            <span className={`account-avatar role-${String(user.role).toLowerCase().replaceAll("/", "-").replaceAll(" ", "-")}`}>
              <UserRoundCog size={28} />
            </span>
            <div>
              <span className="eyebrow">Account Overview</span>
              <h2>{user.name}</h2>
              <p>{user.email}</p>
              <div className="account-chip-row">
                <span>{user.role}</span>
                {(user.role === "Police Officer" || user.role === "Admin/SP") && <span>{user.verification_status || "Verification pending"}</span>}
              </div>
            </div>
          </div>
          <div className="home-account-actions">
            <Link className="button button-primary" to={roleHome(user.role)}>
              <ShieldCheck size={18} />
              {user.role === "Citizen" ? "Go to Citizen Dashboard" : user.role === "Admin/SP" ? "Go to Admin Dashboard" : "Go to Police Dashboard"}
            </Link>
            <Link className="button button-secondary" to="/account">
              Account Details
            </Link>
            <button className="button button-ghost" type="button" onClick={logoutFromHome}>
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </section>
      ) : (
        <section className="demo-accounts-panel" aria-label="Demo accounts for judges">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Judge Demo Access</span>
              <h2>Demo Accounts for Judges</h2>
            </div>
            <span>These are demo credentials for judges. No real personal or police data is used.</span>
          </div>
          <div className="demo-account-grid">
            {demoAccounts.map((account) => (
              <article className="demo-account-card" key={account.email}>
                <strong>{account.title}</strong>
                <div><span>Email</span><a href={`mailto:${account.email}`}>{account.email}</a></div>
                <div><span>Password</span><code>{account.password}</code></div>
                <button className="button button-secondary compact" type="button" onClick={() => continueDemo(account)} disabled={demoLoadingRole === account.role}>
                  <LogIn size={16} />
                  {demoLoadingRole === account.role ? "Signing in..." : account.button}
                </button>
              </article>
            ))}
          </div>
          <div className="demo-verification-code">
            <span>Police Registration Demo Verification Code</span>
            <code>PRAKASAM-POLICE-DEMO</code>
          </div>
          {demoError && <div className="error-banner">{demoError}</div>}
        </section>
      )}

      <section className="module-overview-panel" aria-label="CyberShield Police modules">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">5 Core Modules</span>
            <h2>One Connected Cybercrime Workflow</h2>
          </div>
          <span>Citizen report to automated triage to police case to hotspot and CTI analytics</span>
        </div>
        <div className="module-overview-grid">
          {moduleOverview.map((module) => {
            const Icon = module.icon;
            return (
              <article className="module-card" key={module.title}>
                <Icon size={23} />
                <strong>{module.title}</strong>
                <p>{module.text}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="demo-flow-panel" aria-label="Police demo flow">
        <div className="panel-heading">
          <h2>{t("home.demoFlow")}</h2>
          <span>{t("home.demoFlowSub")}</span>
        </div>
        <div className="demo-flow-grid">
          {demoFlowKeys.map((step, index) => (
            <div className="flow-step" key={step}>
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>

      <div className="section-grid landing-grid">
        <article className="feature-card">
          <ShieldAlert size={24} />
          <h2>{t("home.feature1")}</h2>
          <p>{t("home.feature1Text")}</p>
        </article>
        <article className="feature-card">
          <Database size={24} />
          <h2>{t("home.feature2")}</h2>
          <p>{t("home.feature2Text")}</p>
        </article>
        <article className="feature-card">
          <Radar size={24} />
          <h2>{t("home.feature3")}</h2>
          <p>{t("home.feature3Text")}</p>
        </article>
      </div>

      <div className="sample-strip" aria-label="Supported scam categories">
        {[
          "Phishing",
          "Fake KYC",
          "OTP Fraud",
          "UPI Fraud",
          "Fake Job",
          "Work From Home",
          "Lottery",
          "Investment",
          "Fake Loan",
          "QR Scam",
          "Legal Threat",
        ].map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>

      <section className="why-police-panel">
        <div>
          <span className="eyebrow">Why Police Need This</span>
          <h2>From scattered complaints to explainable triage</h2>
          <p>
            CyberShield Police connects reporting, detection, transaction risk, hotspot intelligence, and case management
            into one prevention-focused prototype for Challenge 05.
          </p>
        </div>
        <div className="why-police-list">
          {policeNeeds.map((item) => (
            <div key={item}>
              <ShieldCheck size={18} />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="wide-callout">
        <div>
          <h2>Built for a solo developer demo</h2>
          <p>
            No paid APIs, no secrets, no real personal data. The prototype uses synthetic examples and a transparent
            detection engine that can be inspected, tuned, and presented confidently.
          </p>
        </div>
        <Link className="button button-ghost" to="/tips">
          Safety Tips
          <ArrowRight size={18} />
        </Link>
      </div>
    </section>
  );
}
