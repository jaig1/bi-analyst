import { useState } from "react";
import api from "../api/client";

export interface QueryResult {
  question: string;
  sql: string;
  chart_type: "bar" | "line" | "pie" | "kpi" | "table";
  chart_data: Record<string, unknown>[];
  x_key: string | null;
  y_keys: string[];
  narrative: string;
  rows: Record<string, unknown>[];
  row_count: number;
  execution_ms: number;
}

export function useQuery() {
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(question: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const { data } = await api.post<QueryResult>("/query", { question });
      setResult(data);
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return { result, loading, error, ask };
}
