import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getChartData } from "../api";

export default function ChartsTab({ datasetId, columns }) {
  const [column, setColumn] = useState(columns?.[0]?.name || "");
  const [chart, setChart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!column) return;
    setLoading(true);
    setError(null);
    getChartData(datasetId, column)
      .then(setChart)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [datasetId, column]);

  return (
    <div className="charts-tab">
      <div className="chart-controls">
        <label htmlFor="col-select" className="section-label">
          Column
        </label>
        <select id="col-select" value={column} onChange={(e) => setColumn(e.target.value)}>
          {columns.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name} {c.is_numeric ? "(numeric)" : "(categorical)"}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="empty-hint">Rendering chart…</p>}
      {error && <p className="upload-error">{error}</p>}

      {chart && !loading && (
        <div className="chart-frame">
          <p className="chart-caption">
            {chart.type === "histogram" ? "Distribution" : "Value counts"} of{" "}
            <b>{chart.column}</b>
          </p>
          <ResponsiveContainer width="100%" height={380}>
            <BarChart data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-soft)" vertical={false} />
              <XAxis
                dataKey="label"
                stroke="var(--text-faint)"
                tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                angle={-35}
                textAnchor="end"
                interval={0}
                height={80}
              />
              <YAxis stroke="var(--text-faint)" tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
              <Tooltip
                contentStyle={{
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  color: "var(--text)",
                  fontFamily: "var(--font-mono)",
                  fontSize: 12,
                }}
                cursor={{ fill: "rgba(255,255,255,0.03)" }}
              />
              <Bar dataKey="value" fill="var(--accent)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
