import React, { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, Bot, ChevronDown, ClipboardList, CreditCard, FileImage, FilePlus2, FileSearch, Home, LayoutDashboard, LogIn, LogOut, Map, Menu, Network, Radar, Search, ShieldCheck, Sparkles, UserCircle, UserPlus, X } from "lucide-react";
import { clearAuth, getStoredUser, roleHome } from "../auth.js";
import AIStatusIndicator from "./AIStatusIndicator.jsx";
import LanguageSelector from "./LanguageSelector.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

const primaryLinks = [
  { to: "/", labelKey: "nav.home", icon: Home, end: true },
  { to: "/report-incident", labelKey: "nav.report", icon: FilePlus2 },
];

const groupedLinks = [
  {
    label: "Tools",
    icon: FileSearch,
    items: [
      { to: "/analyzer", labelKey: "nav.analyzer", icon: FileSearch },
      { to: "/phishing-scanner", labelKey: "nav.phishing", icon: Search },
      { to: "/screenshot-analyzer", label: "Screenshot Analyzer", icon: FileImage },
      { to: "/transactions", labelKey: "nav.transactions", icon: CreditCard },
      { to: "/indicator-lookup", label: "URL/UPI Validator", icon: Search },
    ],
  },
  {
    label: "Intelligence",
    icon: Radar,
    items: [
      { to: "/hotspots", labelKey: "nav.hotspots", icon: Map },
      { to: "/threat-intel", label: "Threat Stream", icon: Radar },
      { to: "/threat-dashboard", label: "Threat Dashboard", icon: BarChart3 },
      { to: "/case-patterns", labelKey: "nav.patterns", icon: Network },
      { to: "/dashboard", labelKey: "nav.dashboard", icon: BarChart3 },
    ],
  },
  {
    label: "Police",
    icon: ClipboardList,
    items: [
      { to: "/police", label: "Police Dashboard", icon: LayoutDashboard },
      { to: "/case-management", labelKey: "nav.cases", icon: ClipboardList },
    ],
  },
];

function NavItem({ item, t, onNavigate }) {
  const Icon = item.icon;
  return (
    <NavLink key={item.to} to={item.to} end={item.end} className="nav-link" onClick={onNavigate}>
      <Icon size={17} />
      <span>{item.label || t(item.labelKey)}</span>
    </NavLink>
  );
}

function NavDropdown({ group, t, onNavigate, openDropdown, setOpenDropdown }) {
  const Icon = group.icon;
  const isOpen = openDropdown === group.label;
  return (
    <details className="nav-dropdown" open={isOpen}>
      <summary
        className="nav-link nav-dropdown-trigger"
        onClick={(event) => {
          event.preventDefault();
          setOpenDropdown(isOpen ? "" : group.label);
        }}
      >
        <Icon size={17} />
        <span>{group.label}</span>
        <ChevronDown size={14} />
      </summary>
      <div className="nav-dropdown-menu">
        {group.items.map((item) => {
          const ItemIcon = item.icon;
          return (
            <NavLink key={item.to} to={item.to} className="nav-menu-link" onClick={onNavigate}>
              <ItemIcon size={16} />
              <span>{item.label || t(item.labelKey)}</span>
            </NavLink>
          );
        })}
      </div>
    </details>
  );
}

export default function Layout() {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const [user, setUser] = useState(getStoredUser());
  const [menuOpen, setMenuOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState("");
  const [accountOpen, setAccountOpen] = useState(false);
  const topbarRef = useRef(null);

  useEffect(() => {
    function syncAuth() {
      setUser(getStoredUser());
    }
    window.addEventListener("cybershield-auth", syncAuth);
    window.addEventListener("storage", syncAuth);
    return () => {
      window.removeEventListener("cybershield-auth", syncAuth);
      window.removeEventListener("storage", syncAuth);
    };
  }, []);

  useEffect(() => {
    function closeExpandedMenus(event) {
      if (topbarRef.current && !topbarRef.current.contains(event.target)) {
        setOpenDropdown("");
        setAccountOpen(false);
        const openDetails = topbarRef.current.querySelectorAll("details[open]");
        openDetails.forEach((item) => {
          item.open = false;
        });
      }
    }
    document.addEventListener("pointerdown", closeExpandedMenus);
    return () => document.removeEventListener("pointerdown", closeExpandedMenus);
  }, []);

  function logout() {
    clearAuth();
    setMenuOpen(false);
    navigate("/login");
  }

  function closeMenu() {
    setMenuOpen(false);
    setOpenDropdown("");
    setAccountOpen(false);
  }

  return (
    <div className="app-shell">
      <header className="topbar" ref={topbarRef}>
        <div className="topbar-inner">
          <NavLink to="/" className="brand" aria-label="CyberShield Police home" onClick={closeMenu}>
            <span className="brand-mark">
              <ShieldCheck size={24} />
            </span>
            <span>
              <strong>CyberShield Police</strong>
              <small>Mission Y4 Prakasam Hackathon 2026</small>
            </span>
          </NavLink>

          <button
            className="menu-toggle"
            type="button"
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((current) => !current)}
          >
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>

          <div className={`topbar-nav-shell ${menuOpen ? "is-open" : ""}`}>
            <nav className="nav-links" aria-label="Primary navigation">
              {primaryLinks.map((link) => <NavItem key={link.to} item={link} t={t} onNavigate={closeMenu} />)}
              {groupedLinks.map((group) => (
                <NavDropdown
                  key={group.label}
                  group={group}
                  t={t}
                  onNavigate={closeMenu}
                  openDropdown={openDropdown}
                  setOpenDropdown={setOpenDropdown}
                />
              ))}
              <NavDropdown
                group={{
                  label: "More",
                  icon: Sparkles,
                  items: [
                    { to: "/awareness", labelKey: "nav.awareness", icon: Sparkles },
                    { to: "/chatbot", labelKey: "nav.cyberDost", icon: Bot },
                  ],
                }}
                t={t}
                onNavigate={closeMenu}
                openDropdown={openDropdown}
                setOpenDropdown={setOpenDropdown}
              />
            </nav>

            <div className="topbar-actions">
              <AIStatusIndicator />
              <LanguageSelector compact />

              {user ? (
                <details className="account-dropdown" open={accountOpen}>
                  <summary
                    className="session-pill"
                    onClick={(event) => {
                      event.preventDefault();
                      setAccountOpen((current) => !current);
                      setOpenDropdown("");
                    }}
                  >
                    <span className={`role-dot role-${String(user.role).toLowerCase().replaceAll("/", "-").replaceAll(" ", "-")}`} />
                    <span>
                      <strong>{user.role}</strong>
                      <small>{user.verification_status || user.name}</small>
                    </span>
                    <ChevronDown size={15} />
                  </summary>
                  <div className="account-menu">
                    <Link to={roleHome(user.role)} onClick={closeMenu}>
                      <LayoutDashboard size={16} />
                      Dashboard
                    </Link>
                    <Link to="/account" onClick={closeMenu}>
                      <UserCircle size={16} />
                      Account Details
                    </Link>
                    <button type="button" onClick={logout}>
                      <LogOut size={16} />
                      Logout
                    </button>
                  </div>
                </details>
              ) : (
                <div className="nav-auth-actions">
                  <Link className="nav-auth-button" to="/login?mode=login" onClick={closeMenu}>
                    <LogIn size={16} />
                    Login
                  </Link>
                  <Link className="nav-auth-button nav-auth-button-primary" to="/login?mode=register" onClick={closeMenu}>
                    <UserPlus size={16} />
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  );
}
