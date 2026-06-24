import React, { useEffect, useRef, useState } from "react";
import { BrainCircuit, ChevronDown } from "lucide-react";
import { api } from "../api.js";

const providerLabels = {
  gemini: "Gemini",
  multi: "Multi AI",
  openrouter: "OpenRouter",
  groq: "Groq",
  huggingface: "Hugging Face",
  local_fallback: "Local",
};

function providerLabel(value) {
  return providerLabels[value] || value || "Local";
}

export default function AIStatusIndicator() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    let mounted = true;
    api.getAiStatus()
      .then((data) => {
        if (mounted) setStatus(data);
      })
      .catch(() => {
        if (mounted) {
          setError("Backend offline");
          setStatus({
            active_provider: "local_fallback",
            ai_explanation_available: false,
            local_detector_available: false,
            mode: "unavailable",
          });
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("pointerdown", closeOnOutsideClick);
    return () => document.removeEventListener("pointerdown", closeOnOutsideClick);
  }, []);

  const activeProvider = providerLabel(status?.active_provider);
  const aiAvailable = Boolean(status?.ai_explanation_available);
  const localDetector = Boolean(status?.local_detector_available);
  const summaryLabel = aiAvailable ? activeProvider : "Local";
  const model = status?.model || "Local rules";
  const fullStatus = `${activeProvider} - ${model}`;

  return (
    <details className="ai-status-dropdown" open={open} ref={dropdownRef}>
      <summary
        className="ai-status-pill"
        title={fullStatus}
        onClick={(event) => {
          event.preventDefault();
          setOpen((current) => !current);
        }}
      >
        <span className={`ai-status-dot ${aiAvailable ? "is-ai" : "is-local"}`} />
        <BrainCircuit size={15} />
        <strong>{localDetector ? summaryLabel : "Offline"}</strong>
        <ChevronDown size={14} />
      </summary>
      <div className="ai-status-menu">
        <div><span>Active provider</span><strong>{activeProvider}</strong></div>
        <div><span>Model</span><strong>{model}</strong></div>
        <div><span>AI explanation available</span><strong>{aiAvailable ? "Yes" : "No"}</strong></div>
        <div><span>Local detector available</span><strong>{localDetector ? "Yes" : "No"}</strong></div>
        <p>{error || status?.fallback || "Local deterministic scoring remains authoritative."}</p>
      </div>
    </details>
  );
}
