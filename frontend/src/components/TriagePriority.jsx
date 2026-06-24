import React from "react";
import { ShieldAlert } from "lucide-react";

const priorityClass = {
  "Low Priority": "priority-low",
  "Review Recommended": "priority-review",
  "High Priority": "priority-high",
  "Critical Immediate Triage": "priority-critical",
};

export function TriagePriority({ priority, explanation, compact = false }) {
  const label = priority || "Review Recommended";

  return (
    <div className={`triage-priority ${compact ? "triage-priority-compact" : ""}`}>
      <span className={`priority-badge ${priorityClass[label] || "priority-review"}`}>
        <ShieldAlert size={compact ? 13 : 15} />
        {label}
      </span>
      {explanation && <p>{explanation}</p>}
    </div>
  );
}
