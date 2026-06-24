const API_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the generic message when the backend returns non-JSON errors.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export const api = {
  login: (payload) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  registerCitizen: (payload) =>
    request("/auth/register/citizen", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  registerPolice: (payload) =>
    request("/auth/register/police", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  logout: () => request("/auth/logout", { method: "POST" }),
  me: (email) => request(`/auth/me?email=${encodeURIComponent(email || "")}`),
  analyze: (payload) =>
    request("/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getCases: () => request("/cases"),
  getCase: (id) => request(`/cases/${id}`),
  getAnalytics: () => request("/analytics"),
  deleteCase: (id) => request(`/cases/${id}`, { method: "DELETE" }),
  exportUrl: (id) => `${API_BASE}/export/${id}`,
  analyzeTransaction: (payload) =>
    request("/transactions/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getTransactions: () => request("/transactions"),
  getTransaction: (id) => request(`/transactions/${id}`),
  getTransactionAnalytics: () => request("/transactions/analytics"),
  getThreatDashboard: () => request("/threat-intel/dashboard"),
  getThreatIncidents: () => request("/threat-intel/incidents"),
  getThreatIntel: () => request("/threat-intel"),
  searchIndicators: (query) => request(`/threat-intel/indicators/search?query=${encodeURIComponent(query || "")}`),
  getThreatClusters: () => request("/threat-intel/clusters"),
  getThreatCluster: (id) => request(`/threat-intel/clusters/${encodeURIComponent(id)}`),
  submitReport: (payload) =>
    request("/reports", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getReports: () => request("/reports"),
  getReport: (id) => request(`/reports/${id}`),
  assignReport: (id, officer_email) =>
    request(`/reports/${id}/assign`, {
      method: "POST",
      body: JSON.stringify({ officer_email }),
    }),
  updateReportStatus: (id, payload) =>
    request(`/reports/${id}/status`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  addReportNote: (id, payload) =>
    request(`/reports/${id}/notes`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  scanPhishing: (payload) =>
    request("/phishing/scan", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  analyzeScreenshot: (payload) =>
    request("/screenshots/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getAiStatus: () => request("/ai/status"),
  testAi: (payload) =>
    request("/ai/test", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getHotspots: (filters = {}) => {
    const query = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") query.set(key, value);
    });
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return request(`/hotspots${suffix}`);
  },
  getAdminAnalytics: () => request("/admin/analytics"),
  getPoliceVerificationRequests: () => request("/admin/police-verification-requests"),
  approvePoliceVerification: (id) => request(`/admin/police-verification/${id}/approve`, { method: "POST" }),
  rejectPoliceVerification: (id) => request(`/admin/police-verification/${id}/reject`, { method: "POST" }),
  chatbotMessage: (payload) =>
    request("/chatbot/message", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getQuiz: () => request("/awareness/quiz"),
  submitQuiz: (payload) =>
    request("/awareness/quiz/submit", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
