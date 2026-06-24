import React, { useEffect, useState } from "react";
import { AlertTriangle, BadgeIndianRupee, Filter, MapPin, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import LoadingState from "../components/LoadingState.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const initialFilters = {
  scam_type: "All",
  risk_level: "All",
  time_range: "All",
  payment_mode: "All",
  min_amount: "",
  max_amount: "",
};

export default function HotspotMapPage() {
  const { t } = useLanguage();
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    api.getHotspots(filters).then(setData).catch((err) => setError(err.message || "Unable to load hotspots."));
  }, [filters]);

  function updateFilter(event) {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  }

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <LoadingState label={t("hotspots.loading")} />;

  const options = data.filters || {};

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">{t("hotspots.eyebrow")}</span>
        <h1>{t("hotspots.title")}</h1>
        <p>{t("hotspots.subtitle")}</p>
      </div>

      <section className="panel hotspot-filter-panel">
        <div className="panel-heading">
          <h2><Filter size={18} /> {t("hotspots.filters")}</h2>
          <span>{t("hotspots.syntheticNote")}</span>
        </div>
        <div className="form-grid">
          <label><span>{t("hotspots.scamType")}</span><select name="scam_type" value={filters.scam_type} onChange={updateFilter}>{(options.scam_types || ["All"]).map((item) => <option key={item}>{item}</option>)}</select></label>
          <label><span>{t("hotspots.riskLevel")}</span><select name="risk_level" value={filters.risk_level} onChange={updateFilter}>{(options.risk_levels || ["All"]).map((item) => <option key={item}>{item}</option>)}</select></label>
          <label><span>{t("hotspots.timeRange")}</span><select name="time_range" value={filters.time_range} onChange={updateFilter}>{(options.time_ranges || ["All"]).map((item) => <option key={item}>{item}</option>)}</select></label>
          <label><span>{t("hotspots.paymentMode")}</span><select name="payment_mode" value={filters.payment_mode} onChange={updateFilter}>{(options.payment_modes || ["All"]).map((item) => <option key={item}>{item}</option>)}</select></label>
          <label><span>{t("hotspots.minAmount")}</span><input name="min_amount" value={filters.min_amount} onChange={updateFilter} type="number" min="0" placeholder="0" /></label>
          <label><span>{t("hotspots.maxAmount")}</span><input name="max_amount" value={filters.max_amount} onChange={updateFilter} type="number" min="0" placeholder={t("hotspots.noLimit")} /></label>
        </div>
        <button className="button button-ghost" type="button" onClick={() => setFilters(initialFilters)}>{t("hotspots.resetFilters")}</button>
      </section>

      <div className="stats-grid">
        <article className="stat-card"><MapPin size={24} /><span>{t("hotspots.hotspotAreas")}</span><strong>{data.total_hotspots}</strong></article>
        <article className="stat-card"><AlertTriangle size={24} /><span>{t("hotspots.filteredIncidents")}</span><strong>{data.total_incidents}</strong></article>
        <article className="stat-card"><BadgeIndianRupee size={24} /><span>{t("hotspots.syntheticAmount")}</span><strong>Rs. {Number(data.total_synthetic_amount_lost || 0).toLocaleString("en-IN")}</strong></article>
        <article className="stat-card"><TrendingUp size={24} /><span>{t("hotspots.topArea")}</span><strong>{data.top_affected_locations?.[0]?.location || "None"}</strong></article>
      </div>

      <section className="panel map-style-panel">
        <div className="panel-heading">
          <h2>{t("hotspots.mapLayout")}</h2>
          <span>{t("hotspots.mapLayoutSub")}</span>
        </div>
        <div className="hotspot-grid">
          {data.hotspots.map((hotspot) => (
            <article className={`hotspot-card heat-${hotspot.heat_level.toLowerCase()}`} key={hotspot.location}>
              <MapPin size={24} />
              <strong>{hotspot.location}</strong>
              <span>{hotspot.heat_level} {t("hotspots.heat")}</span>
              <p>{hotspot.incident_count} {t("hotspots.syntheticIncidents")}: {hotspot.top_category}</p>
              <small>{t("hotspots.demoAmount")}: Rs. {Number(hotspot.total_amount_lost).toLocaleString("en-IN")}</small>
            </article>
          ))}
        </div>
      </section>

      <div className="dashboard-grid">
        <section className="panel chart-panel">
          <div className="panel-heading"><h2>{t("hotspots.amountByArea")}</h2><span>{t("hotspots.lossDistribution")}</span></div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.amount_lost_by_area || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={74} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#be123c" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
        <section className="panel chart-panel">
          <div className="panel-heading"><h2>{t("hotspots.incidentsOverTime")}</h2><span>{t("hotspots.filteredTrend")}</span></div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.incidents_over_time || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d8e0ea" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={74} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#1d4ed8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading"><h2>{t("hotspots.insightsAlerts")}</h2><span>{t("hotspots.observations")}</span></div>
        <div className="cluster-mini-grid">
          {(data.insights || []).map((insight) => <div className="cluster-mini-card" key={insight}><strong>{insight}</strong><span>{t("hotspots.trendInsight")}</span></div>)}
          {(data.high_risk_area_alerts || []).map((alert) => <div className="cluster-mini-card alert-card" key={alert}><strong>{alert}</strong><span>{t("hotspots.highRiskAlert")}</span></div>)}
        </div>
      </section>
    </section>
  );
}
