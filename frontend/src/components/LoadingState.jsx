import React from "react";

export default function LoadingState({ label = "Loading" }) {
  return (
    <div className="loading-state" role="status">
      <span className="loader" />
      <strong>{label}</strong>
      <span>Preparing the local CyberShield workspace</span>
    </div>
  );
}
