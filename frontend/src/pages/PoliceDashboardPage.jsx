import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertOctagon, BadgeIndianRupee, ClipboardList, FileSearch, FolderCheck, Map, RadioTower, Radar, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskBadge } from "../components/RiskBadge.jsx";
import { CaseSummaryCard, PageHeader, SectionCard, StatCard, StatusBadge } from "../components/ProductUI.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

export default function PoliceDashboardPage() {
  const { t } = useLanguage();
  const [reports, setReports] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getReports(), api.getAnalytics()])
      .then(([reportData, caseAnalytics]) => {
        setReports(reportData);
        setAnalytics(caseAnalytics);
      })
      .catch((err) => setError(err.message || "Unable to load police dashboard."));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!reports || !analytics) return <LoadingState label={t("dashboard.loadingPoliceQueue")} />;

  const priorityReports = reports.filter((report) =>
    ["High Priority", "Critical Immediate Triage"].includes(report.police_triage_priority)
  );
  const statusCounts = reports.reduce((counts, report) => {
    const status = report.status || "New";
    counts[status] = (counts[status] || 0) + 1;
    return counts;
  }, {});
  const locationCounts = reports.reduce((counts, report) => {
    const location = report.location || "Unknown";
    counts[location] = (counts[location] || 0) + 1;
    return counts;
  }, {});
  const topLocations = Object.entries(locationCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  const totalSyntheticAmount = reports.reduce((sum, report) => sum + Number(report.transaction_amount || 0), 0);
  const urgentReports = priorityReports.slice(0, 3);

  const statCards = [
    { label: "New Reports", value: statusCounts.New || 0, icon: ClipboardList, tone: "blue" },
    { label: "Under Review", value: statusCounts["Under Review"] || 0, icon: RadioTower, tone: "teal" },
    { label: "Verified Scam", value: statusCounts["Verified Scam"] || 0, icon: FolderCheck, tone: "green" },
    { label: "Escalated", value: statusCounts.Escalated || 0, icon: AlertOctagon, tone: "rose" },
    { label: "Closed Cases", value: statusCounts.Closed || statusCounts["Closed - Awareness Given"] || 0, icon: FolderCheck, tone: "slate" },
    { label: "Synthetic Amount", value: `Rs. ${totalSyntheticAmount.toLocaleString("en-IN")}`, icon: BadgeIndianRupee, tone: "amber" },
  ];

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow={t("dashboard.police")}
        title={t("dashboard.investigationQueue")}
        subtitle="A police-facing triage queue for complaints, evidence metadata, officer notes, FIR draft support, and synthetic threat intelligence context."
      />

      <div className="role-action-grid">
        <Link className="role-action-card" to="/case-management">
          <ClipboardList size={24} />
          <strong>{t("dashboard.caseManagement")}</strong>
          <span>{t("dashboard.caseManagementSub")}</span>
        </Link>
        <Link className="role-action-card" to="/analyzer">
          <FileSearch size={24} />
          <strong>{t("nav.analyzer")}</strong>
          <span>{t("dashboard.scamAnalyzerSub")}</span>
        </Link>
        <Link className="role-action-card" to="/hotspots">
          <Map size={24} />
          <strong>{t("dashboard.hotspotMap")}</strong>
          <span>{t("dashboard.hotspotMapSub")}</span>
        </Link>
        <Link className="role-action-card" to="/threat-intel">
          <Radar size={24} />
          <strong>{t("dashboard.threatIntel")}</strong>
          <span>{t("dashboard.threatIntelSub")}</span>
        </Link>
      </div>

      <div className="stats-grid police-stat-grid">
        <StatCard label={t("dashboard.citizenReports")} value={reports.length} icon={ClipboardList} tone="blue" />
        <StatCard label={t("dashboard.highRiskScamCases")} value={analytics.high_risk_reports} icon={ShieldAlert} tone="rose" />
        <StatCard label={t("dashboard.priorityReports")} value={priorityReports.length} icon={AlertOctagon} tone="amber" />
        {statCards.map((card) => <StatCard key={card.label} {...card} />)}
      </div>

      <div className="dashboard-grid">
        <SectionCard title="Recent Urgent Complaints" subtitle="Automated summaries for police triage">
          <div className="case-summary-list">
            {(urgentReports.length ? urgentReports : reports.slice(0, 3)).map((report) => (
              <CaseSummaryCard key={report.id} report={report} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Location Intelligence" subtitle="Synthetic complaint concentration">
          <div className="location-rank-list">
            {topLocations.map(([location, count], index) => (
              <div key={location}>
                <span>{index + 1}</span>
                <strong>{location}</strong>
                <small>{count} reports</small>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>{t("dashboard.highPriorityReports")}</h2>
          <span>{t("dashboard.openReportHint")}</span>
        </div>
        <div className="table-wrap">
          <table className="case-table">
            <thead>
              <tr>
                <th>{t("citizen.trackingId")}</th>
                <th>{t("common.category")}</th>
                <th>{t("common.risk")}</th>
                <th>{t("dashboard.priority")}</th>
                <th>{t("common.status")}</th>
              </tr>
            </thead>
            <tbody>
              {(priorityReports.length ? priorityReports : reports).slice(0, 10).map((report) => (
                <tr key={report.id}>
                  <td><Link to={`/case-management/${report.id}`}>{report.tracking_id}</Link></td>
                  <td>{report.detected_category}</td>
                  <td><RiskBadge level={report.risk_level} score={report.risk_score} /></td>
                  <td>{report.police_triage_priority}</td>
                  <td><StatusBadge status={report.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
