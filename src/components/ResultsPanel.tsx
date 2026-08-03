import { useState } from "react";
import type { QueryResult } from "../hooks/useQuery";
import ChartRenderer from "./ChartRenderer";

interface Props {
  result: QueryResult;
}

export default function ResultsPanel({ result }: Props) {
  const [showSql, setShowSql] = useState(false);
  const columns = result.rows.length > 0 ? Object.keys(result.rows[0]) : [];

  return (
    <div style={styles.card}>
      {/* Question */}
      <p style={styles.question}>"{result.question}"</p>

      {/* Narrative */}
      <div style={styles.narrative}>{result.narrative}</div>

      {/* Chart */}
      {result.chart_type !== "table" && (
        <div style={styles.chartWrap}>
          <ChartRenderer
            chartType={result.chart_type}
            data={result.chart_data}
            xKey={result.x_key}
            yKeys={result.y_keys}
          />
        </div>
      )}

      {/* Data table */}
      {result.rows.length > 0 && (
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col} style={styles.th}>
                    {col.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.rows.map((row, i) => (
                <tr key={i} style={i % 2 === 0 ? styles.rowEven : styles.rowOdd}>
                  {columns.map((col) => (
                    <td key={col} style={styles.td}>
                      {String(row[col] ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Meta + SQL toggle */}
      <div style={styles.meta}>
        <span>{result.row_count} rows · {result.execution_ms}ms</span>
        <button style={styles.sqlToggle} onClick={() => setShowSql((s) => !s)}>
          {showSql ? "Hide SQL" : "Show SQL"}
        </button>
      </div>

      {showSql && (
        <pre style={styles.sql}>{result.sql}</pre>
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
    marginBottom: 20,
  },
  question: {
    fontSize: 17,
    fontWeight: 600,
    color: "#1a1a2e",
    marginBottom: 14,
  },
  narrative: {
    background: "#f0fdf4",
    border: "1px solid #bbf7d0",
    borderRadius: 8,
    padding: "14px 18px",
    fontSize: 14,
    lineHeight: 1.65,
    color: "#166534",
    marginBottom: 20,
  },
  chartWrap: {
    marginBottom: 20,
  },
  tableWrap: {
    overflowX: "auto",
    marginBottom: 16,
    borderRadius: 8,
    border: "1px solid #e5e7eb",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 13,
  },
  th: {
    background: "#f9fafb",
    padding: "10px 14px",
    textAlign: "left",
    fontWeight: 600,
    color: "#374151",
    textTransform: "capitalize",
    borderBottom: "1px solid #e5e7eb",
    whiteSpace: "nowrap",
  },
  td: {
    padding: "9px 14px",
    color: "#374151",
    borderBottom: "1px solid #f3f4f6",
  },
  rowEven: { background: "#fff" },
  rowOdd:  { background: "#fafafa" },
  meta: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontSize: 12,
    color: "#9ca3af",
  },
  sqlToggle: {
    background: "none",
    border: "1px solid #e5e7eb",
    borderRadius: 6,
    padding: "4px 10px",
    fontSize: 12,
    cursor: "pointer",
    color: "#6b7280",
  },
  sql: {
    marginTop: 12,
    background: "#1e1e2e",
    color: "#cdd6f4",
    borderRadius: 8,
    padding: "16px 18px",
    fontSize: 12,
    overflowX: "auto",
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
  },
};
