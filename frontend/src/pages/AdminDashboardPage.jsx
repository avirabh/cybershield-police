import React, { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, Database, ShieldAlert, UserRoundCog, XCircle } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";

export default function AdminDashboardPage() {
  const [data, setData] = useState(null);
  const [verificationRequests, setVerificationRequests] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getAdminAnalytics(), api.getPoliceVerificationRequests()])
      .then(([analytics, requests]) => {
        setData(analytics);
        setVerificationRequests(requests);
      })
      .catch((err) => setError(err.message || "Unable to load admin analytics."));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <LoadingState label="Loading Admin/SP view" />;

  const cards = [
    { label: "Incident Reports", value: data.total_incident_reports, icon: Database },
    { label: "Scam Cases", value: data.total_scam_cases, icon: ShieldAlert },
    { label: "Transactions", value: data.total_transactions, icon: Activity },
    { label: "Critical Queue", value: data.critical_queue_count, icon: UserRoundCog },
  ];

  async function updateVerification(id, action) {
    const updated =
      action === "approve"
        ? await api.approvePoliceVerification(id)
        : await api.rejectPoliceVerification(id);
    setVerificationRequests((current) => current.map((item) => (item.id === updated.id ? updated : item)));
  }

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Admin/SP Oversight</span>
        <h1>Command Analytics</h1>
        <p>Supervise workload, priority queues, synthetic trends, and demo system health from one view.</p>
      </div>
      <div className="stats-grid">
        {cards.map((card) => {
          const Icon = card.icon;
          return <article className="stat-card" key={card.label}><Icon size={24} /><span>{card.label}</span><strong>{card.value}</strong></article>;
        })}
      </div>
      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading"><h2>Status Distribution</h2><span>Citizen reports by status</span></div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.status_distribution}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="value" fill="#1d4ed8" /></BarChart>
          </ResponsiveContainer>
        </section>
        <section className="panel chart-panel">
          <div className="panel-heading"><h2>Officer Workload</h2><span>Assigned demo reports</span></div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.officer_workload}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="value" fill="#0f766e" /></BarChart>
          </ResponsiveContainer>
        </section>
      </div>
      <section className="panel">
        <div className="panel-heading">
          <h2>Police Account Verification Requests</h2>
          <span>Mock Admin/SP approval for hackathon demo accounts</span>
        </div>
        <div className="table-wrap">
          <table className="case-table verification-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Rank</th>
                <th>Station / Unit</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {verificationRequests.map((request) => (
                <tr key={request.id}>
                  <td>{request.name}</td>
                  <td>{request.email}</td>
                  <td>{request.rank_designation || "Demo placeholder"}</td>
                  <td>{request.police_station || "Demo placeholder"}</td>
                  <td>
                    <span className={`status-pill status-${String(request.verification_status || "").toLowerCase().replaceAll(" ", "-")}`}>
                      {request.verification_status}
                    </span>
                  </td>
                  <td>
                    <div className="table-action-row">
                      <button
                        className="icon-button success"
                        type="button"
                        onClick={() => updateVerification(request.id, "approve")}
                        title="Approve police demo account"
                      >
                        <CheckCircle2 size={16} />
                      </button>
                      <button
                        className="icon-button danger"
                        type="button"
                        onClick={() => updateVerification(request.id, "reject")}
                        title="Reject police demo account"
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading"><h2>System Health</h2><span>Synthetic-only public demo readiness</span></div>
        <div className="detail-list">
          <div><span>Database</span><strong>{data.system_health.database}</strong></div>
          <div><span>External APIs</span><strong>{data.system_health.external_api_dependency}</strong></div>
          <div><span>Data Policy</span><strong>{data.system_health.data_policy}</strong></div>
          <div><span>Top Location</span><strong>{data.top_location}</strong></div>
        </div>
      </section>
    </section>
  );
}
