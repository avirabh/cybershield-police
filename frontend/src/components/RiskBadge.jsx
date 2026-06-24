import React from "react";

const levelClass = {
  Low: "risk-low",
  Medium: "risk-medium",
  High: "risk-high",
  Critical: "risk-critical",
};

export function RiskBadge({ level }) {
  return <span className={`risk-badge ${levelClass[level] || "risk-low"}`}>{level || "Low"}</span>;
}

export function RiskMeter({ score = 0, level = "Low" }) {
  const clamped = Math.max(0, Math.min(100, Number(score) || 0));

  return (
    <div className="risk-meter" aria-label={`Risk score ${clamped} out of 100`}>
      <div className="risk-meter-top">
        <div>
          <span>Risk Score</span>
          <strong>{clamped}/100</strong>
        </div>
        <RiskBadge level={level} />
      </div>
      <div className="meter-track">
        <div className={`meter-fill ${levelClass[level] || "risk-low"}`} style={{ width: `${clamped}%` }} />
      </div>
      <div className="risk-scale">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
        <span>Critical</span>
      </div>
    </div>
  );
}
