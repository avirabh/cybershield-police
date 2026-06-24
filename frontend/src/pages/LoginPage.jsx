import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Eye, EyeOff, Landmark, LogIn, ShieldCheck, UserPlus, UserRound, UserRoundCog } from "lucide-react";
import { api } from "../api.js";
import { roleHome, saveAuth } from "../auth.js";
import LanguageSelector from "../components/LanguageSelector.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const demoUsers = [
  { label: "Login as Citizen", role: "Citizen", email: "citizen@example.com", password: "citizen123" },
  { label: "Login as Police Officer", role: "Police Officer", email: "officer@example.com", password: "officer123" },
  { label: "Login as Admin/SP", role: "Admin/SP", email: "admin@example.com", password: "admin123" },
];

const citizenInitial = {
  name: "",
  email: "",
  password: "",
  location: "",
  age_group: "Adult",
};

const policeInitial = {
  name: "",
  email: "",
  rank_designation: "",
  police_station: "",
  district: "Prakasam",
  badge_id_placeholder: "",
  verification_document_name: "",
  verification_code: "",
  password: "",
};

function AuthField({ label, children }) {
  return (
    <label>
      <span>{label}</span>
      {children}
    </label>
  );
}

export default function LoginPage() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryRole = searchParams.get("role");
  const queryMode = searchParams.get("mode");
  const initialRole = queryRole === "Police Officer" || queryRole === "Admin/SP" ? "Police Officer" : "Citizen";
  const initialMode = queryMode === "register" ? "register" : "login";
  const [roleMode, setRoleMode] = useState(initialRole);
  const [formMode, setFormMode] = useState(initialMode);
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [citizenForm, setCitizenForm] = useState(citizenInitial);
  const [policeForm, setPoliceForm] = useState(policeInitial);
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setRoleMode(queryRole === "Police Officer" || queryRole === "Admin/SP" ? "Police Officer" : "Citizen");
    setFormMode(queryMode === "register" ? "register" : "login");
  }, [queryMode, queryRole]);

  function routeAfterAuth(payload) {
    saveAuth(payload);
    if (payload.user.role === "Police Officer" && payload.user.verification_status !== "Verified") {
      navigate("/verification-pending");
      return;
    }
    navigate(roleHome(payload.user.role));
  }

  async function submitLogin(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const payload = await api.login(loginForm);
      routeAfterAuth(payload);
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  async function submitCitizen(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const payload = await api.registerCitizen(citizenForm);
      setMessage("Citizen account created. Redirecting to dashboard.");
      routeAfterAuth(payload);
    } catch (err) {
      setError(err.message || "Citizen registration failed.");
    } finally {
      setLoading(false);
    }
  }

  async function submitPolice(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const payload = await api.registerPolice(policeForm);
      setMessage(payload.message);
      routeAfterAuth(payload);
    } catch (err) {
      setError(err.message || "Police registration failed.");
    } finally {
      setLoading(false);
    }
  }

  function demoLogin(user) {
    setRoleMode(user.role === "Admin/SP" ? "Police Officer" : user.role);
    setFormMode("login");
    setLoginForm({ email: user.email, password: user.password });
  }

  const passwordType = showPassword ? "text" : "password";

  return (
    <section className="auth-showcase">
      <div className="auth-hero-card">
        <div className="auth-language-row">
          <span className="eyebrow">CyberShield Police</span>
          <LanguageSelector compact />
        </div>
        <h1>{t("login.heroTitle")}</h1>
        <p>{t("common.tagline")}</p>
        <div className="auth-role-switch">
          <button className={roleMode === "Citizen" ? "active" : ""} type="button" onClick={() => setRoleMode("Citizen")}>
            <UserRound size={18} />
            {t("login.citizenLogin")}
          </button>
          <button className={roleMode === "Police Officer" ? "active" : ""} type="button" onClick={() => setRoleMode("Police Officer")}>
            <Landmark size={18} />
            {t("login.policeLogin")}
          </button>
        </div>
        <div className="demo-login-panel">
          <strong>{t("login.demoLogin")}</strong>
          <div className="demo-login-buttons">
            {demoUsers.map((user) => (
              <button type="button" key={user.email} onClick={() => demoLogin(user)}>
                <UserRoundCog size={17} />
                {user.role === "Citizen" ? t("login.loginCitizen") : user.role === "Admin/SP" ? t("login.loginAdmin") : t("login.loginPolice")}
              </button>
            ))}
          </div>
        </div>
        <div className="auth-note">
          {t("login.mockNote")}
        </div>
      </div>

      <div className="panel auth-panel auth-main-panel">
        <div className="auth-tabs">
          <button className={formMode === "login" ? "active" : ""} type="button" onClick={() => setFormMode("login")}>{t("common.login")}</button>
          <button className={formMode === "register" ? "active" : ""} type="button" onClick={() => setFormMode("register")}>{t("common.register")}</button>
        </div>

        {formMode === "login" && (
          <form className="auth-form-stack" onSubmit={submitLogin}>
            <div className="auth-form-heading">
              <ShieldCheck size={28} />
              <div>
                <h2>{roleMode === "Citizen" ? t("login.citizenLogin") : t("login.policeAdminLogin")}</h2>
                <span className="role-badge">{roleMode}</span>
              </div>
            </div>
            <AuthField label={t("common.email")}>
              <input value={loginForm.email} onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))} type="email" placeholder={t("login.enterEmail")} required />
            </AuthField>
            <AuthField label={t("common.password")}>
              <div className="password-field">
                <input value={loginForm.password} onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))} type={passwordType} placeholder={t("login.enterPassword")} required />
                <button type="button" onClick={() => setShowPassword((current) => !current)} aria-label="Toggle password visibility">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </AuthField>
            {error && <div className="error-banner">{error}</div>}
            {message && <div className="success-banner">{message}</div>}
            <button className="button button-primary" type="submit" disabled={loading}>
              <LogIn size={18} />
              {loading ? t("common.loading") : t("common.signIn")}
            </button>
          </form>
        )}

        {formMode === "register" && roleMode === "Citizen" && (
          <form className="auth-form-stack" onSubmit={submitCitizen}>
            <div className="auth-form-heading">
              <UserPlus size={28} />
              <div>
                <h2>{t("login.citizenRegistration")}</h2>
                <span className="role-badge citizen">{t("login.verifiedDemo")}</span>
              </div>
            </div>
            <div className="form-grid two-column">
              <AuthField label={t("common.name")}><input value={citizenForm.name} onChange={(event) => setCitizenForm((current) => ({ ...current, name: event.target.value }))} required /></AuthField>
              <AuthField label={t("common.email")}><input value={citizenForm.email} onChange={(event) => setCitizenForm((current) => ({ ...current, email: event.target.value }))} type="email" required /></AuthField>
              <AuthField label={t("login.locationMandal")}><input value={citizenForm.location} onChange={(event) => setCitizenForm((current) => ({ ...current, location: event.target.value }))} placeholder="Ongole" /></AuthField>
              <AuthField label={t("common.ageGroup")}>
                <select value={citizenForm.age_group} onChange={(event) => setCitizenForm((current) => ({ ...current, age_group: event.target.value }))}>
                  <option>Student</option>
                  <option>Adult</option>
                  <option>Senior Citizen</option>
                  <option>Business Owner</option>
                </select>
              </AuthField>
            </div>
            <AuthField label={t("common.password")}><input value={citizenForm.password} onChange={(event) => setCitizenForm((current) => ({ ...current, password: event.target.value }))} type={passwordType} required /></AuthField>
            {error && <div className="error-banner">{error}</div>}
            <button className="button button-primary" type="submit" disabled={loading}><UserPlus size={18} />{t("login.createCitizen")}</button>
          </form>
        )}

        {formMode === "register" && roleMode === "Police Officer" && (
          <form className="auth-form-stack" onSubmit={submitPolice}>
            <div className="auth-form-heading">
              <Landmark size={28} />
              <div>
                <h2>{t("login.policeRegistration")}</h2>
                <span className="role-badge police">{t("login.mockVerification")}</span>
              </div>
            </div>
            <div className="form-grid two-column">
              <AuthField label={t("login.fullName")}><input value={policeForm.name} onChange={(event) => setPoliceForm((current) => ({ ...current, name: event.target.value }))} required /></AuthField>
              <AuthField label={t("login.officialEmail")}><input value={policeForm.email} onChange={(event) => setPoliceForm((current) => ({ ...current, email: event.target.value }))} type="email" required /></AuthField>
              <AuthField label={t("login.rank")}><input value={policeForm.rank_designation} onChange={(event) => setPoliceForm((current) => ({ ...current, rank_designation: event.target.value }))} placeholder="Sub Inspector" /></AuthField>
              <AuthField label={t("login.station")}><input value={policeForm.police_station} onChange={(event) => setPoliceForm((current) => ({ ...current, police_station: event.target.value }))} placeholder="Ongole Cyber Desk" /></AuthField>
              <AuthField label={t("login.district")}><input value={policeForm.district} onChange={(event) => setPoliceForm((current) => ({ ...current, district: event.target.value }))} /></AuthField>
              <AuthField label={t("login.badge")}><input value={policeForm.badge_id_placeholder} onChange={(event) => setPoliceForm((current) => ({ ...current, badge_id_placeholder: event.target.value }))} placeholder="DEMO-BADGE-123" /></AuthField>
            </div>
            <AuthField label={t("login.document")}>
              <input value={policeForm.verification_document_name} onChange={(event) => setPoliceForm((current) => ({ ...current, verification_document_name: event.target.value }))} placeholder="demo-document-placeholder.pdf" />
            </AuthField>
            <AuthField label={t("login.inviteCode")}>
              <input value={policeForm.verification_code} onChange={(event) => setPoliceForm((current) => ({ ...current, verification_code: event.target.value }))} placeholder="PRAKASAM-POLICE-DEMO for instant demo verification" />
            </AuthField>
            <AuthField label={t("common.password")}><input value={policeForm.password} onChange={(event) => setPoliceForm((current) => ({ ...current, password: event.target.value }))} type={passwordType} required /></AuthField>
            {error && <div className="error-banner">{error}</div>}
            {message && <div className="success-banner">{message}</div>}
            <button className="button button-primary" type="submit" disabled={loading}><UserPlus size={18} />{t("login.createPolice")}</button>
          </form>
        )}
      </div>
    </section>
  );
}
