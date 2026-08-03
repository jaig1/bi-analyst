import { useState, KeyboardEvent } from "react";

const SUGGESTIONS = [
  "What were my top 5 products last quarter?",
  "Which customers haven't reordered in 90 days?",
  "Where are we losing margin? Show by category.",
  "What is total revenue by region this year?",
  "Show me monthly revenue for the past 6 months.",
];

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

export default function QueryInput({ onSubmit, loading }: Props) {
  const [value, setValue] = useState("");

  function submit(q?: string) {
    const question = (q ?? value).trim();
    if (!question || loading) return;
    setValue("");
    onSubmit(question);
  }

  function handleKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div style={styles.wrapper}>
      <p style={styles.label}>Ask a question about your business data</p>

      {/* Suggestion chips */}
      <div style={styles.chips}>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            style={styles.chip}
            onClick={() => submit(s)}
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div style={styles.inputRow}>
        <textarea
          style={styles.textarea}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          placeholder="e.g. What were my top 5 products last quarter?"
          rows={2}
          disabled={loading}
        />
        <button
          style={{ ...styles.btn, opacity: loading || !value.trim() ? 0.5 : 1 }}
          onClick={() => submit()}
          disabled={loading || !value.trim()}
        >
          {loading ? "Thinking…" : "Ask"}
        </button>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    background: "#fff",
    borderRadius: 12,
    padding: "24px 28px",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
    marginBottom: 24,
  },
  label: {
    fontSize: 13,
    color: "#666",
    marginBottom: 12,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  chips: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 16,
  },
  chip: {
    background: "#f0f2f5",
    border: "1px solid #e0e4ea",
    borderRadius: 20,
    padding: "6px 14px",
    fontSize: 13,
    cursor: "pointer",
    color: "#444",
    transition: "background 0.15s",
  },
  inputRow: {
    display: "flex",
    gap: 12,
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    border: "1.5px solid #d0d5dd",
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 15,
    resize: "vertical",
    outline: "none",
    fontFamily: "inherit",
    lineHeight: 1.5,
  },
  btn: {
    background: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "10px 24px",
    fontSize: 15,
    cursor: "pointer",
    fontWeight: 600,
    whiteSpace: "nowrap",
    height: 44,
  },
};
