import { useEffect, useState } from "react";
import api from "../api/client";

interface AuditEntry {
  id: number;
  user_id: string;
  user_role: string;
  question: string;
  generated_sql: string;
  row_count: number | null;
  execution_ms: number | null;
  chart_type: string | null;
  created_at: string;
}

export default function AuditLog() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/audit/logs?page=${page}&page_size=15`)
      .then(({ data }) => {
        setEntries(data.entries);
        setTotal(data.total);
        setError(null);
      })
      .catch(() => setError("Failed to load audit log"))
      .finally(() => setLoading(false));
  }, [page]);

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>Query Audit Log</h2>
      <p style={styles.sub}>{total} total queries logged</p>

      {error && <p style={styles.error}>{error}</p>}
      {loading && <p style={{ color: "#aaa" }}>Loading…</p>}

      {!loading && entries.length > 0 && (
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                {["Time", "User", "Role", "Question", "Chart", "Rows", "ms"].map((h) => (
                  <th key={h} style={styles.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => (
                <tr key={e.id} style={i % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                  <td style={styles.td}>{new Date(e.created_at).toLocaleString()}</td>
                  <td style={styles.td}>{e.user_id}</td>
                  <td style={styles.td}>{e.user_role}</td>
                  <td style={{ ...styles.td, maxWidth: 320 }}>{e.question}</td>
                  <td style={styles.td}>{e.chart_type ?? "—"}</td>
                  <td style={styles.td}>{e.row_count ?? "—"}</td>
                  <td style={styles.td}>{e.execution_ms ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {total > 15 && (
        <div style={styles.pagination}>
          <button
            style={styles.pageBtn}
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Prev
          </button>
          <span style={{ fontSize: 13, color: "#666" }}>
            Page {page} of {Math.ceil(total / 15)}
          </span>
          <button
            style={styles.pageBtn}
            disabled={page >= Math.ceil(total / 15)}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#fff",
    borderRadius: 12,
    padding: "24px 28px",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
  },
  title: { fontSize: 18, fontWeight: 700, marginBottom: 4 },
  sub: { fontSize: 13, color: "#9ca3af", marginBottom: 16 },
  error: { color: "#dc2626", fontSize: 13, marginBottom: 12 },
  tableWrap: { overflowX: "auto", borderRadius: 8, border: "1px solid #e5e7eb" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 13 },
  th: {
    background: "#f9fafb",
    padding: "10px 12px",
    textAlign: "left",
    fontWeight: 600,
    color: "#374151",
    borderBottom: "1px solid #e5e7eb",
    whiteSpace: "nowrap",
  },
  td: { padding: "9px 12px", color: "#374151", borderBottom: "1px solid #f3f4f6" },
  rowEven: { background: "#fff" },
  rowOdd:  { background: "#fafafa" },
  pagination: {
    display: "flex",
    gap: 16,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 16,
  },
  pageBtn: {
    background: "#f0f2f5",
    border: "1px solid #e0e4ea",
    borderRadius: 6,
    padding: "6px 14px",
    cursor: "pointer",
    fontSize: 13,
  },
};
