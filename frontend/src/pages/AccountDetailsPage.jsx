import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, ShieldCheck, UserRoundCog } from "lucide-react";
import { clearAuth, getStoredUser, roleHome } from "../auth.js";

function DetailRow({ label, value }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value || "Demo placeholder"}</strong>
    </div>
  );
}

export default function AccountDetailsPage() {
  const navigate = useNavigate();
  const user = getStoredUser();

  function logout() {
    clearAuth();
    navigate("/");
  }

  if (!user) {
    return (
      <section className="page-stack">
        <div className="panel account-details-card">
          <ShieldCheck size={34} />
          <h1>Account Details</h1>
          <p>You are not logged in. Use demo credentials or register a demo account to continue.</p>
          <Link className="button button-primary" to="/login">
            Login
          </Link>
        </div>
      </section>
    );
  }

  const isOfficer = user.role === "Police Officer" || user.role === "Admin/SP";

  return (
    <section className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">Demo Account</span>
        <h1>Account Details</h1>
        <p>Mock authentication profile for hackathon evaluation. Passwords are never shown after login.</p>
      </div>

      <section className="panel account-details-card">
        <div className="account-details-header">
          <span className={`account-avatar role-${String(user.role).toLowerCase().replaceAll("/", "-").replaceAll(" ", "-")}`}>
            <UserRoundCog size={28} />
          </span>
          <div>
            <span className="eyebrow">{user.role}</span>
            <h2>{user.name}</h2>
            <p>{user.email}</p>
          </div>
        </div>

        <div className="detail-list account-detail-list">
          <DetailRow label="Name" value={user.name} />
          <DetailRow label="Email" value={user.email} />
          <DetailRow label="Role" value={user.role} />
          <DetailRow label="Account Type" value="Hackathon demo account" />
          {user.role === "Citizen" && <DetailRow label="Location / Mandal" value={user.location} />}
          {user.role === "Citizen" && <DetailRow label="Age Group" value={user.age_group} />}
          {isOfficer && <DetailRow label="Station / Unit" value={user.police_station} />}
          {isOfficer && <DetailRow label="Rank / Designation" value={user.rank_designation} />}
          {isOfficer && <DetailRow label="District" value={user.district} />}
          {isOfficer && <DetailRow label="Verification Status" value={user.verification_status} />}
        </div>

        <div className="auth-note">
          Authentication is mock/demo-based for hackathon evaluation. No real personal or police data is used.
        </div>

        <div className="form-actions">
          <Link className="button button-primary" to={roleHome(user.role)}>
            <ShieldCheck size={18} />
            Go to Dashboard
          </Link>
          <button className="button button-ghost" type="button" onClick={logout}>
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </section>
    </section>
  );
}
