import React from "react";
import { Link } from "react-router-dom";
import { Clock, ShieldAlert } from "lucide-react";
import { getStoredUser } from "../auth.js";

export default function VerificationPendingPage() {
  const user = getStoredUser();

  return (
    <section className="pending-layout">
      <div className="panel pending-panel">
        <Clock size={42} />
        <span className="eyebrow">Verification Pending</span>
        <h1>Police Account Under Demo Review</h1>
        <p>
          {user?.name || "This police account"} is registered, but full police dashboard access is locked until
          Admin/SP approval or the demo verification code is used during registration.
        </p>
        <div className="detail-list">
          <div><span>Status</span><strong>{user?.verification_status || "Pending Verification"}</strong></div>
          <div><span>Email</span><strong>{user?.email || "Not available"}</strong></div>
          <div><span>Station / Unit</span><strong>{user?.police_station || "Demo placeholder"}</strong></div>
          <div><span>Demo Code</span><strong>PRAKASAM-POLICE-DEMO</strong></div>
        </div>
        <div className="emergency-guidance">
          <ShieldAlert size={18} />
          <span>No real police ID verification is performed. This is a safe hackathon mock workflow.</span>
        </div>
        <div className="form-actions">
          <Link className="button button-secondary" to="/login">Back to Login</Link>
          <Link className="button button-ghost" to="/">Home</Link>
        </div>
      </div>
    </section>
  );
}
