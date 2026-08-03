import { useState } from "react";
import api from "./api/client";
import QueryInput from "./components/QueryInput";
import ResultsPanel from "./components/ResultsPanel";
import AuditLog from "./components/AuditLog";
import { useQuery } from "./hooks/useQuery";

type View = "analyst" | "audit";

interface AuthState {
  token: string;
  role: string;
  userId: string;
}

export default function App() {
  const [auth, setAuth] = useState<AuthState | null>(() => {
    const token = sessionStorage.getItem("token");
    const role = sessionStorage.getItem("role");
    const userId = sessionStorage.getItem("userId");
    return token && role && userId ? { token, role, userId } : null;
  });
  const [view, setView] = useState<View>("analyst");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  const { result, loading, error, ask } = useQuery();

  // ── Login form ──────────────────────────────────────────────────────────
  if (!auth) {
    return (
      <div style={styles.loginPage}>
        <div style={styles.loginCard}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>📊</span>
            <h1 style={styles.logoTitle}>AI BI Analyst</h1>
          </div>
          <p style={styles.loginSub}>Sign in to ask questions about your business data.</p>

          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              const username = fd.get("username") as string;
              const password = fd.get("password") as string;
              setLoginLoading(true);
              setLoginError(null);
              try {
                const { data } = await api.post("/auth/login", { username, password });
                sessionStorage.setItem("token", data.access_token);
                sessionStorage.setItem("role", data.role);
                sessionStorage.setItem("userId", data.user_id);
                setAuth({ token: data.access_token, role: data.role, userId: data.user_id });
              } catch {
                setLoginError("Invalid credentials. Try owner@demo.com / demo1234");
              } finally {
                setLoginLoading(false);
              }
            }}
          >
            <input style={styles.input} name="username" type="email"
              placeholder="Email" defaultValue="owner@demo.com" required />
            <input style={styles.input} name="password" type="password"
              placeholder="Password" defaultValue="demo1234" required />
            {loginError && <p style={styles.err}>{loginError}</p>}
            <button style={styles.loginBtn} type="submit" disabled={loginLoading}>
              {loginLoading ? "Signing in…" : "Sign In"}
            </button>
          </form>

          <div style={styles.demoHint}>
            <strong>Demo accounts:</strong><br />
            owner@demo.com · manager@demo.com · staff@demo.com<br />
            Password: <code>demo1234</code>
          </div>
        </div>
      </div>
    );
  }

  // ── Main app ────────────────────────────────────────────────────────────
  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.headerLeft}>
            <span style={{ fontSize: 22 }}>📊</span>
            <span style={styles.headerTitle}>AI BI Analyst</span>
          </div>
          <nav style={styles.nav}>
            <button
              style={{ ...styles.navBtn, ...(view === "analyst" ? styles.navActive : {}) }}
              onClick={() => setView("analyst")}
            >
              Ask a Question
            </button>
            {auth.role === "owner" && (
              <button
                style={{ ...styles.navBtn, ...(view === "audit" ? styles.navActive : {}) }}
                onClick={() => setView("audit")}
              >
                Audit Log
              </button>
            )}
          </nav>
          <div style={styles.userBadge}>
            <span style={styles.rolePill}>{auth.role}</span>
            <button
              style={styles.signOut}
              onClick={() => {
                sessionStorage.clear();
                setAuth(null);
              }}
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main style={styles.main}>
        {view === "analyst" ? (
          <>
            <QueryInput onSubmit={ask} loading={loading} />

            {loading && (
              <div style={styles.loadingBox}>
                <div style={styles.spinner} />
                <span>Analysing your data…</span>
              </div>
            )}

            {error && (
              <div style={styles.errorBox}>{error}</div>
            )}

            {result && !loading && (
              <ResultsPanel result={result} />
            )}
          </>
        ) : (
          <AuditLog />
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  // ── Login
  loginPage: {
    minHeight: "100vh", display: "flex", alignItems: "center",
    justifyContent: "center", background: "#f0f2f5",
  },
  loginCard: {
    background: "#fff", borderRadius: 16, padding: "40px 44px",
    boxShadow: "0 4px 24px rgba(0,0,0,0.1)", width: "100%", maxWidth: 420,
  },
  logo: { display: "flex", alignItems: "center", gap: 10, marginBottom: 8 },
  logoIcon: { fontSize: 32 },
  logoTitle: { fontSize: 22, fontWeight: 700, color: "#1a1a2e" },
  loginSub: { color: "#6b7280", fontSize: 14, marginBottom: 24 },
  input: {
    display: "block", width: "100%", padding: "11px 14px",
    border: "1.5px solid #d0d5dd", borderRadius: 8,
    fontSize: 15, marginBottom: 12, fontFamily: "inherit", outline: "none",
  },
  err: { color: "#dc2626", fontSize: 13, marginBottom: 10 },
  loginBtn: {
    width: "100%", padding: "12px", background: "#4f46e5", color: "#fff",
    border: "none", borderRadius: 8, fontSize: 15, fontWeight: 600,
    cursor: "pointer", marginTop: 4,
  },
  demoHint: {
    marginTop: 20, padding: "12px 16px", background: "#f9fafb",
    borderRadius: 8, fontSize: 12, color: "#6b7280", lineHeight: 1.7,
    border: "1px solid #e5e7eb",
  },

  // ── App shell
  app: { display: "flex", flexDirection: "column", minHeight: "100vh" },
  header: {
    background: "#fff", borderBottom: "1px solid #e5e7eb",
    position: "sticky", top: 0, zIndex: 10,
  },
  headerInner: {
    maxWidth: 1100, margin: "0 auto", padding: "0 24px",
    display: "flex", alignItems: "center", justifyContent: "space-between",
    height: 58,
  },
  headerLeft: { display: "flex", alignItems: "center", gap: 10 },
  headerTitle: { fontSize: 17, fontWeight: 700, color: "#1a1a2e" },
  nav: { display: "flex", gap: 4 },
  navBtn: {
    background: "none", border: "none", padding: "6px 14px",
    borderRadius: 6, cursor: "pointer", fontSize: 14, color: "#6b7280",
  },
  navActive: { background: "#ede9fe", color: "#4f46e5", fontWeight: 600 },
  userBadge: { display: "flex", alignItems: "center", gap: 10 },
  rolePill: {
    background: "#f0fdf4", color: "#166534", border: "1px solid #bbf7d0",
    borderRadius: 20, padding: "3px 10px", fontSize: 12, fontWeight: 600,
    textTransform: "capitalize",
  },
  signOut: {
    background: "none", border: "1px solid #e5e7eb", borderRadius: 6,
    padding: "5px 12px", fontSize: 12, cursor: "pointer", color: "#6b7280",
  },
  main: { flex: 1, maxWidth: 1100, margin: "0 auto", padding: "28px 24px", width: "100%" },

  // ── Loading / error
  loadingBox: {
    display: "flex", alignItems: "center", gap: 14,
    background: "#fff", borderRadius: 12, padding: "24px 28px",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)", color: "#6b7280", fontSize: 14,
  },
  spinner: {
    width: 20, height: 20,
    border: "3px solid #e5e7eb", borderTopColor: "#4f46e5",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
  },
  errorBox: {
    background: "#fef2f2", border: "1px solid #fecaca",
    borderRadius: 10, padding: "16px 20px", color: "#991b1b",
    fontSize: 14, marginBottom: 16,
  },
};
