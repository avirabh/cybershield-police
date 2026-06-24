import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bot, ClipboardList, FilePlus2, FileSearch, GraduationCap, ShieldAlert } from "lucide-react";
import { api } from "../api.js";
import { getStoredUser } from "../auth.js";
import LoadingState from "../components/LoadingState.jsx";
import { RiskBadge } from "../components/RiskBadge.jsx";
import LanguageSelector from "../components/LanguageSelector.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

export default function CitizenDashboardPage() {
  const { t } = useLanguage();
  const user = getStoredUser();
  const [reports, setReports] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getReports().then(setReports).catch((err) => setError(err.message || "Unable to load reports."));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!reports) return <LoadingState label={`${t("common.loading")} citizen dashboard`} />;

  const ownReports = reports.filter((report) => {
    if (!user?.name) return true;
    return report.reporter_name === user.name || report.reporter_name === "Demo Citizen";
  });
  const priorityCount = ownReports.filter((report) =>
    ["High Priority", "Critical Immediate Triage"].includes(report.police_triage_priority)
  ).length;

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div className="heading-with-control">
          <span className="eyebrow">{t("citizen.portal")}</span>
          <LanguageSelector compact />
        </div>
        <h1>{t("citizen.welcome")}, {user?.name || "Demo Citizen"}</h1>
        <p>{t("citizen.subtitle")}</p>
      </div>

      <div className="role-action-grid">
        <Link className="role-action-card" to="/report-incident">
          <FilePlus2 size={24} />
          <strong>{t("citizen.reportTitle")}</strong>
          <span>{t("citizen.reportText")}</span>
        </Link>
        <Link className="role-action-card" to="/analyzer">
          <FileSearch size={24} />
          <strong>{t("citizen.checkTitle")}</strong>
          <span>{t("citizen.checkText")}</span>
        </Link>
        <Link className="role-action-card" to="/chatbot">
          <Bot size={24} />
          <strong>Cyber Dost Prakasam</strong>
          <span>{t("citizen.cyberDostText")}</span>
        </Link>
        <Link className="role-action-card" to="/awareness">
          <GraduationCap size={24} />
          <strong>{t("citizen.awarenessTitle")}</strong>
          <span>{t("citizen.awarenessText")}</span>
        </Link>
      </div>

      <div className="stats-grid">
        <article className="stat-card">
          <ClipboardList size={24} />
          <span>{t("citizen.myReports")}</span>
          <strong>{ownReports.length}</strong>
        </article>
        <article className="stat-card">
          <ShieldAlert size={24} />
          <span>{t("citizen.priorityQueue")}</span>
          <strong>{priorityCount}</strong>
        </article>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>{t("citizen.recentStatus")}</h2>
          <span>{t("citizen.fictionalOnly")}</span>
        </div>
        <div className="table-wrap">
          <table className="case-table">
            <thead>
              <tr>
                <th>{t("citizen.trackingId")}</th>
                <th>{t("common.category")}</th>
                <th>{t("common.risk")}</th>
                <th>{t("common.status")}</th>
                <th>{t("citizen.assignedOfficer")}</th>
              </tr>
            </thead>
            <tbody>
              {ownReports.slice(0, 8).map((report) => (
                <tr key={report.id}>
                  <td>{report.tracking_id}</td>
                  <td>{report.detected_category}</td>
                  <td><RiskBadge level={report.risk_level} score={report.risk_score} /></td>
                  <td>{report.status}</td>
                  <td>{report.assigned_officer || t("citizen.unassigned")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
