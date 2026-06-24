import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { getStoredUser, roleHome } from "./auth.js";
import Layout from "./components/Layout.jsx";
import AdminDashboardPage from "./pages/AdminDashboardPage.jsx";
import AccountDetailsPage from "./pages/AccountDetailsPage.jsx";
import AnalyzerPage from "./pages/AnalyzerPage.jsx";
import AwarenessHubPage from "./pages/AwarenessHubPage.jsx";
import CasePatternAnalyzerPage from "./pages/CasePatternAnalyzerPage.jsx";
import CaseDetailsPage from "./pages/CaseDetailsPage.jsx";
import CaseManagementPage from "./pages/CaseManagementPage.jsx";
import ChatbotPage from "./pages/ChatbotPage.jsx";
import CitizenDashboardPage from "./pages/CitizenDashboardPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import HotspotMapPage from "./pages/HotspotMapPage.jsx";
import IndicatorLookupPage from "./pages/IndicatorLookupPage.jsx";
import IncidentReportPage from "./pages/IncidentReportPage.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import PhishingScannerPage from "./pages/PhishingScannerPage.jsx";
import PoliceDashboardPage from "./pages/PoliceDashboardPage.jsx";
import ScreenshotAnalyzerPage from "./pages/ScreenshotAnalyzerPage.jsx";
import ThreatIntelligencePage from "./pages/ThreatIntelligencePage.jsx";
import TipsPage from "./pages/TipsPage.jsx";
import ThreatDashboardPage from "./pages/ThreatDashboardPage.jsx";
import TransactionMonitorPage from "./pages/TransactionMonitorPage.jsx";
import VerificationPendingPage from "./pages/VerificationPendingPage.jsx";

function ProtectedRoute({ roles, requireVerifiedPolice = false, children }) {
  const user = getStoredUser();
  if (!user) return <Navigate to="/login" replace />;
  if (roles?.length && !roles.includes(user.role)) return <Navigate to={roleHome(user.role)} replace />;
  if (
    requireVerifiedPolice &&
    user.role === "Police Officer" &&
    user.verification_status !== "Verified"
  ) {
    return <Navigate to="/verification-pending" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/account" element={<AccountDetailsPage />} />
        <Route path="/verification-pending" element={<VerificationPendingPage />} />
        <Route path="/citizen" element={<ProtectedRoute roles={["Citizen"]}><CitizenDashboardPage /></ProtectedRoute>} />
        <Route path="/police" element={<ProtectedRoute roles={["Police Officer", "Admin/SP"]} requireVerifiedPolice><PoliceDashboardPage /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute roles={["Admin/SP"]}><AdminDashboardPage /></ProtectedRoute>} />
        <Route path="/report-incident" element={<ProtectedRoute roles={["Citizen"]}><IncidentReportPage /></ProtectedRoute>} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
        <Route path="/phishing-scanner" element={<PhishingScannerPage />} />
        <Route path="/screenshot-analyzer" element={<ScreenshotAnalyzerPage />} />
        <Route path="/transactions" element={<TransactionMonitorPage />} />
        <Route path="/hotspots" element={<HotspotMapPage />} />
        <Route path="/threat-intel" element={<ThreatIntelligencePage />} />
        <Route path="/threat-dashboard" element={<ThreatDashboardPage />} />
        <Route path="/indicator-lookup" element={<IndicatorLookupPage />} />
        <Route path="/case-patterns" element={<CasePatternAnalyzerPage />} />
        <Route path="/case-management" element={<ProtectedRoute roles={["Police Officer", "Admin/SP"]} requireVerifiedPolice><CaseManagementPage /></ProtectedRoute>} />
        <Route path="/case-management/:id" element={<ProtectedRoute roles={["Police Officer", "Admin/SP"]} requireVerifiedPolice><CaseManagementPage /></ProtectedRoute>} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/cases/:id" element={<CaseDetailsPage />} />
        <Route path="/awareness" element={<AwarenessHubPage />} />
        <Route path="/quiz" element={<AwarenessHubPage />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/tips" element={<TipsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
