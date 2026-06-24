import React, { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AlertOctagon, BadgeIndianRupee, ClipboardList, CreditCard, FileText, Layers, Link2, MapPin, Network, RadioTower, Radar, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import CaseTable from "../components/CaseTable.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { RiskBadge } from "../components/RiskBadge.jsx";
import TransactionTable from "../components/TransactionTable.jsx";

const COLORS = ["#0f766e", "#1d4ed8", "#b45309", "#be123c", "#6d28d9", "#047857", "#c2410c", "#334155"];

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [transactionData, setTransactionData] = useState(null);
  const [threatData, setThreatData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getAnalytics(), api.getTransactionAnalytics(), api.getThreatDashboard()])
      .then(([caseAnalytics, transactionAnalytics, threatAnalytics]) => {
        setData(caseAnalytics);
        setTransactionData(transactionAnalytics);
        setThreatData(threatAnalytics);
      })
      .catch((err) => setError(err.message || "Unable to load dashboard."));
  }, []);

  if (error) {
    return (
      <section className="page-stack">
        <div className="error-banner">{error}</div>
      </section>
    );
  }

  if (!data || !transactionData || !threatData) {
    return <LoadingState label="Loading police dashboard" />;
  }

  const categoryDistribution = data.category_distribution || [];
  const platformDistribution = data.platform_distribution || [];
  const riskLevelDistribution = data.risk_level_distribution || [];
  const topRiskFactors = data.top_risk_factors || [];
  const highPriorityCases = data.high_priority_cases || [];
  const criticalAlerts = data.critical_alerts || [];
  const recentCases = data.recent_cases || [];
  const transactionRiskDistribution = transactionData.risk_level_distribution || [];
  const suspiciousTransactionCategories = transactionData.suspicious_transaction_categories || [];
  const highPriorityTransactions = transactionData.high_priority_transactions || [];
  const recentTransactions = transactionData.recent_transactions || [];
  const linkedClusters = threatData.linked_case_clusters || [];

  const statCards = [
    { label: "Total Reports", value: data.total_reports, icon: Layers },
    { label: "High Risk Reports", value: data.high_risk_reports, icon: ShieldAlert },
    { label: "Critical Reports", value: data.critical_reports, icon: AlertOctagon },
    { label: "Text-Only Scams", value: data.text_only_scam_count ?? 0, icon: FileText },
    { label: "URL-Based Scams", value: data.url_based_scam_count ?? 0, icon: Link2 },
    { label: "High Priority", value: highPriorityCases.length, icon: ClipboardList },
    { label: "Avg Confidence", value: `${data.average_confidence ?? 0}%`, icon: RadioTower },
  ];

  const transactionStatCards = [
    { label: "Monitored Transactions", value: transactionData.total_transactions, icon: CreditCard },
    { label: "High-Risk Transactions", value: transactionData.high_risk_transaction_count, icon: ShieldAlert },
    { label: "Critical Transactions", value: transactionData.critical_transaction_count, icon: AlertOctagon },
    {
      label: "Total Monitored Amount",
      value: `Rs. ${Number(transactionData.total_monitored_amount || 0).toLocaleString("en-IN")}`,
      icon: BadgeIndianRupee,
    },
    { label: "Transaction Priority Queue", value: transactionData.high_priority_transaction_count, icon: ClipboardList },
  ];

  const threatStatCards = [
    { label: "Synthetic Incidents", value: threatData.total_incidents, icon: Radar },
    { label: "High-Risk Indicators", value: threatData.high_risk_indicators_count, icon: ShieldAlert },
    { label: "Active Fraud Clusters", value: threatData.active_clusters_count, icon: Network },
    { label: "Top Scam Category", value: threatData.top_scam_category, icon: AlertOctagon },
    { label: "Top Location", value: threatData.top_affected_location, icon: MapPin },
  ];

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Police Operations View</span>
        <h1>Cybercrime Dashboard</h1>
        <p>Monitor report volume, scam categories, platform patterns, and urgent alerts from synthetic demo cases.</p>
      </div>

      <div className="dashboard-brief">
        <div>
          <strong>Text intelligence</strong>
          <span>Plain SMS, call notes, WhatsApp, and email are counted even without URLs.</span>
        </div>
        <div>
          <strong>Explainable triage</strong>
          <span>Priority is based on risk score, category severity, and matched evidence.</span>
        </div>
        <div>
          <strong>Demo-safe data</strong>
          <span>Analytics are powered by fictional synthetic cases only.</span>
        </div>
      </div>

      <div className="section-label">
        <h2>Scam Message Analytics</h2>
        <span>Messages, links, and citizen reports</span>
      </div>

      <div className="stats-grid">
        {statCards.map((item) => {
          const Icon = item.icon;
          return (
            <article className="stat-card" key={item.label}>
              <Icon size={24} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          );
        })}
      </div>

      <div className="section-label">
        <h2>Transaction Monitoring Analytics</h2>
        <span>Synthetic payment-risk signals</span>
      </div>

      <div className="stats-grid">
        {transactionStatCards.map((item) => {
          const Icon = item.icon;
          return (
            <article className="stat-card" key={item.label}>
              <Icon size={24} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          );
        })}
      </div>

      <div className="section-label">
        <h2>Cyber Threat Intelligence</h2>
        <span>{threatData.weekly_trend_insight}</span>
      </div>

      <div className="stats-grid">
        {threatStatCards.map((item) => {
          const Icon = item.icon;
          return (
            <article className="stat-card" key={item.label}>
              <Icon size={24} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          );
        })}
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>Linked Fraud Clusters</h2>
          <span>Pattern intelligence from synthetic cases</span>
        </div>
        <div className="cluster-mini-grid">
          {linkedClusters.slice(0, 4).map((cluster) => (
            <div className="cluster-mini-card" key={cluster.cluster_id}>
              <strong>{cluster.cluster_name}</strong>
              <span>{cluster.linked_case_count} linked cases</span>
              <p>{cluster.suspected_fraud_pattern}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Transaction Risk Levels</h2>
            <span>Low to critical payment patterns</span>
          </div>
          {transactionRiskDistribution.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={transactionRiskDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#be123c" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">No transaction risk data yet.</p>
          )}
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Suspicious Transaction Categories</h2>
            <span>Detected payment scam patterns</span>
          </div>
          {suspiciousTransactionCategories.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={suspiciousTransactionCategories}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={88} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#0f766e" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">No transaction category data yet.</p>
          )}
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>High Priority Transactions</h2>
          <span>Payment triage queue</span>
        </div>
        <TransactionTable
          transactions={highPriorityTransactions}
          emptyMessage="No high-priority transactions in the current queue."
        />
      </section>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Category Distribution</h2>
            <span>Cases by scam type</span>
          </div>
          {categoryDistribution.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={categoryDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={80} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#1d4ed8" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">No category data yet. Seed demo cases or analyze a message.</p>
          )}
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Platform Distribution</h2>
            <span>Source channels</span>
          </div>
          {platformDistribution.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={platformDistribution}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={62}
                  outerRadius={96}
                  paddingAngle={3}
                >
                  {platformDistribution.map((entry, index) => (
                    <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">No platform data yet. Seed demo cases or analyze a message.</p>
          )}
        </section>
      </div>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Risk Level Distribution</h2>
            <span>Low to critical</span>
          </div>
          {riskLevelDistribution.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={riskLevelDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} fill="#b45309" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">No risk-level data yet.</p>
          )}
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Top Risk Factors</h2>
            <span>Most triggered rules</span>
          </div>
          {topRiskFactors.length ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={topRiskFactors} layout="vertical" margin={{ left: 20, right: 18 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis dataKey="name" type="category" width={130} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} fill="#0f766e" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="empty-state">Risk factors will appear after analysis cases are stored.</p>
          )}
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>High Priority Cases</h2>
          <span>Police triage queue</span>
        </div>
        <CaseTable cases={highPriorityCases} emptyMessage="No high-priority cases in the current queue." />
      </section>

      <section className="panel alerts-panel">
        <div className="panel-heading">
          <h2>Critical Alerts</h2>
          <span>Score 80 and above</span>
        </div>
        {criticalAlerts.length ? (
          <div className="alert-list">
            {criticalAlerts.map((item) => (
              <div className="alert-row" key={item.id}>
                <div>
                  <strong>Case #{item.id} - {item.category}</strong>
                  <p>{(item.message || "No message text stored.").slice(0, 120)}{(item.message || "").length > 120 ? "..." : ""}</p>
                </div>
                <RiskBadge level={item.risk_level} />
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">No critical alerts at the moment.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Recent Cases</h2>
          <span>Latest stored reports</span>
        </div>
        <CaseTable cases={recentCases} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Recent Monitored Transactions</h2>
          <span>Latest synthetic transaction reports</span>
        </div>
        <TransactionTable transactions={recentTransactions} />
      </section>
    </section>
  );
}
