import React, { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AlertTriangle, Filter, MapPin, Radar } from "lucide-react";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";

function amountLabel(value) {
  return `Rs. ${Number(value || 0).toLocaleString("en-IN")}`;
}

function distribution(items, key) {
  const counts = new Map();
  items.forEach((item) => counts.set(item[key] || "Unknown", (counts.get(item[key] || "Unknown") || 0) + 1));
  return Array.from(counts, ([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

function amountDistribution(items, key) {
  const counts = new Map();
  items.forEach((item) => counts.set(item[key] || "Unknown", (counts.get(item[key] || "Unknown") || 0) + Number(item.amount_lost || 0)));
  return Array.from(counts, ([name, value]) => ({ name, value: Math.round(value) })).sort((a, b) => b.value - a.value);
}

export default function ThreatDashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    scamType: "All",
    amountRange: "All",
    timeRange: "All",
    paymentMode: "All",
  });

  useEffect(() => {
    Promise.all([api.getThreatDashboard(), api.getThreatIncidents()])
      .then(([dashboardData, incidentData]) => {
        setDashboard(dashboardData);
        setIncidents(incidentData);
      })
      .catch((err) => setError(err.message || "Unable to load threat intelligence dashboard."));
  }, []);

  function updateFilter(event) {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  }

  const scamTypes = useMemo(() => ["All", ...new Set(incidents.map((item) => item.scam_type))], [incidents]);
  const paymentModes = useMemo(() => ["All", ...new Set(incidents.map((item) => item.payment_mode))], [incidents]);

  const filtered = useMemo(() => {
    return incidents.filter((incident) => {
      if (filters.scamType !== "All" && incident.scam_type !== filters.scamType) return false;
      if (filters.paymentMode !== "All" && incident.payment_mode !== filters.paymentMode) return false;
      const amount = Number(incident.amount_lost || 0);
      if (filters.amountRange === "Under 5000" && amount >= 5000) return false;
      if (filters.amountRange === "5000-20000" && (amount < 5000 || amount > 20000)) return false;
      if (filters.amountRange === "Above 20000" && amount <= 20000) return false;
      const day = Number(String(incident.incident_date || "").slice(-2));
      if (filters.timeRange === "Last 7 demo days" && day < 15) return false;
      if (filters.timeRange === "First 7 demo days" && day > 7) return false;
      return true;
    });
  }, [filters, incidents]);

  if (error) {
    return (
      <section className="page-stack">
        <div className="error-banner">
          <AlertTriangle size={18} />
          {error}
        </div>
      </section>
    );
  }

  if (!dashboard) {
    return <LoadingState label="Loading threat intelligence" />;
  }

  const locationChart = distribution(filtered, "location");
  const categoryChart = distribution(filtered, "scam_type");
  const amountChart = amountDistribution(filtered, "scam_type");
  const trendChart = dashboard.incidents_over_time || [];

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Cyber Threat Intelligence</span>
        <h1>Threat Intelligence Dashboard</h1>
        <p>Map-style synthetic incident intelligence for Prakasam and Andhra Pradesh, designed for safe police demo workflows.</p>
      </div>

      <div className="stats-grid">
        <article className="stat-card">
          <Radar size={24} />
          <span>Total Synthetic Incidents</span>
          <strong>{dashboard.total_incidents}</strong>
        </article>
        <article className="stat-card">
          <MapPin size={24} />
          <span>Top Affected Location</span>
          <strong>{dashboard.top_affected_location}</strong>
        </article>
        <article className="stat-card">
          <Filter size={24} />
          <span>Total Synthetic Amount</span>
          <strong>{amountLabel(dashboard.total_amount_lost)}</strong>
        </article>
      </div>

      <section className="panel cti-filter-panel">
        <div className="panel-heading">
          <h2>Filters</h2>
          <span>Client-side demo filtering</span>
        </div>
        <div className="form-grid">
          <label>
            <span>Scam type</span>
            <select name="scamType" value={filters.scamType} onChange={updateFilter}>
              {scamTypes.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            <span>Amount range</span>
            <select name="amountRange" value={filters.amountRange} onChange={updateFilter}>
              <option>All</option>
              <option>Under 5000</option>
              <option>5000-20000</option>
              <option>Above 20000</option>
            </select>
          </label>
          <label>
            <span>Time range</span>
            <select name="timeRange" value={filters.timeRange} onChange={updateFilter}>
              <option>All</option>
              <option>First 7 demo days</option>
              <option>Last 7 demo days</option>
            </select>
          </label>
          <label>
            <span>Payment mode</span>
            <select name="paymentMode" value={filters.paymentMode} onChange={updateFilter}>
              {paymentModes.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
        </div>
      </section>

      <div className="trend-grid">
        {dashboard.trend_cards.map((card) => (
          <article className="trend-card" key={card.title}>
            <span>{card.title}</span>
            <strong>{card.value}</strong>
            <p>{card.detail}</p>
          </article>
        ))}
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>Prakasam Incident Heat View</h2>
          <span>Mandal/city-wise synthetic fraud heat</span>
        </div>
        <div className="heat-grid">
          {dashboard.heat_indicators.map((item) => (
            <div className={`heat-tile heat-${item.heat.toLowerCase()}`} key={item.location}>
              <strong>{item.location}</strong>
              <span>{item.incidents} incidents</span>
              <span>{amountLabel(item.total_amount)}</span>
              <em>{item.heat}</em>
            </div>
          ))}
        </div>
      </section>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Incidents By Location</h2>
            <span>{filtered.length} filtered incidents</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={locationChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={80} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#1d4ed8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Incidents By Scam Category</h2>
            <span>Synthetic case mix</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categoryChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={86} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f766e" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Incidents Over Time</h2>
            <span>Demo reporting trend</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trendChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#be123c" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </section>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <h2>Amount Lost By Scam Type</h2>
            <span>Synthetic loss value</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={amountChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={86} />
              <YAxis />
              <Tooltip formatter={(value) => amountLabel(value)} />
              <Bar dataKey="value" fill="#b45309" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>Recent Synthetic Incidents</h2>
          <span>Safe demo intelligence records</span>
        </div>
        <div className="table-wrap">
          <table className="case-table">
            <thead>
              <tr>
                <th>Incident</th>
                <th>Location</th>
                <th>Scam Type</th>
                <th>Payment Mode</th>
                <th>Amount</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 10).map((incident) => (
                <tr key={incident.incident_id}>
                  <td>
                    <strong>{incident.incident_id}</strong>
                    <span>{incident.summary}</span>
                  </td>
                  <td>{incident.location}</td>
                  <td>{incident.scam_type}</td>
                  <td>{incident.payment_mode}</td>
                  <td>{amountLabel(incident.amount_lost)}</td>
                  <td>{incident.risk_level}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
