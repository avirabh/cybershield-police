const STORAGE_KEY = "cybershield_demo_auth";

export function getStoredAuth() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
  } catch {
    return null;
  }
}

export function getStoredUser() {
  return getStoredAuth()?.user || null;
}

export function saveAuth(payload) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  window.dispatchEvent(new Event("cybershield-auth"));
}

export function clearAuth() {
  localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new Event("cybershield-auth"));
}

export function roleHome(role) {
  if (role === "Police Officer") return "/police";
  if (role === "Admin/SP") return "/admin";
  return "/citizen";
}
