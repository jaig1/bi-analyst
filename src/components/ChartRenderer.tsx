import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const COLOURS = [
  "#4f46e5", "#06b6d4", "#10b981", "#f59e0b",
  "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6",
];

interface Props {
  chartType: "bar" | "line" | "pie" | "kpi" | "table";
  data: Record<string, unknown>[];
  xKey: string | null;
  yKeys: string[];
}

export default function ChartRenderer({ chartType, data, xKey, yKeys }: Props) {
  if (!data.length) return null;

  if (chartType === "kpi") {
    return (
      <div style={styles.kpiRow}>
        {yKeys.map((key) => (
          <div key={key} style={styles.kpiCard}>
            <span style={styles.kpiValue}>
              {formatValue(data[0][key])}
            </span>
            <span style={styles.kpiLabel}>{friendlyLabel(key)}</span>
          </div>
        ))}
      </div>
    );
  }

  if (chartType === "bar" && xKey) {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 48 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12 }}
            angle={-30}
            textAnchor="end"
            interval={0}
          />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={compactNum} />
          <Tooltip formatter={(v) => formatValue(v)} />
          <Legend />
          {yKeys.map((key, i) => (
            <Bar key={key} dataKey={key} name={friendlyLabel(key)}
              fill={COLOURS[i % COLOURS.length]} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "line" && xKey) {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 24, left: 8, bottom: 48 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} angle={-30} textAnchor="end" interval={0} />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={compactNum} />
          <Tooltip formatter={(v) => formatValue(v)} />
          <Legend />
          {yKeys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={friendlyLabel(key)}
              stroke={COLOURS[i % COLOURS.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "pie" && xKey && yKeys[0]) {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            dataKey={yKeys[0]}
            nameKey={xKey}
            cx="50%"
            cy="50%"
            outerRadius={120}
            label={({ name, percent }) =>
              `${name} ${(percent * 100).toFixed(1)}%`
            }
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLOURS[i % COLOURS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => formatValue(v)} />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  // "table" fallback — handled by ResultsPanel, but render nothing here
  return null;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function friendlyLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatValue(v: unknown): string {
  if (typeof v === "number") {
    return v >= 1000
      ? new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(v)
      : v.toFixed(2).replace(/\.00$/, "");
  }
  return String(v ?? "");
}

function compactNum(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
  return String(v);
}

const styles: Record<string, React.CSSProperties> = {
  kpiRow: {
    display: "flex",
    gap: 16,
    flexWrap: "wrap",
    margin: "16px 0",
  },
  kpiCard: {
    flex: "1 1 160px",
    background: "#f5f3ff",
    border: "1px solid #e0e7ff",
    borderRadius: 10,
    padding: "20px 24px",
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: 6,
  },
  kpiValue: {
    fontSize: 32,
    fontWeight: 700,
    color: "#4f46e5",
  },
  kpiLabel: {
    fontSize: 13,
    color: "#6b7280",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
};
