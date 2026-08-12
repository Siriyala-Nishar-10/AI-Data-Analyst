function pctBar(pct, color) {
  return (
    <div className="mini-bar-track">
      <div className="mini-bar-fill" style={{ width: `${pct}%`, background: color }} />
    </div>
  );
}

export default function OverviewTab({ summary }) {
  if (!summary) return null;

  const { row_count, column_count, duplicate_rows, columns, correlation } = summary;

  return (
    <div className="overview">
      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Rows</span>
          <span className="stat-value">{row_count.toLocaleString()}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Columns</span>
          <span className="stat-value">{column_count}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Duplicate rows</span>
          <span className="stat-value">{duplicate_rows}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Numeric columns</span>
          <span className="stat-value">{columns.filter((c) => c.is_numeric).length}</span>
        </div>
      </div>

      <h3 className="panel-title">Columns</h3>
      <div className="column-grid">
        {columns.map((col) => (
          <div key={col.name} className="column-card">
            <div className="column-card-head">
              <span className="column-name">{col.name}</span>
              <span className={`dtype-pill ${col.is_numeric ? "dtype-numeric" : "dtype-text"}`}>
                {col.dtype}
              </span>
            </div>

            {col.is_numeric ? (
              <div className="column-stats-row">
                <span>min <b>{col.stats.min}</b></span>
                <span>max <b>{col.stats.max}</b></span>
                <span>mean <b>{col.stats.mean}</b></span>
                <span>median <b>{col.stats.median}</b></span>
              </div>
            ) : (
              <div className="column-top-values">
                {col.top_values.slice(0, 3).map((tv) => (
                  <span key={tv.value} className="top-value-chip">
                    {tv.value} <b>{tv.count}</b>
                  </span>
                ))}
              </div>
            )}

            <div className="missing-row">
              <span>missing {col.missing_count} ({col.missing_pct}%)</span>
              {pctBar(col.missing_pct, "var(--accent-2)")}
            </div>
          </div>
        ))}
      </div>

      {correlation && (
        <>
          <h3 className="panel-title">Correlation</h3>
          <div className="corr-table-wrap">
            <table className="corr-table">
              <thead>
                <tr>
                  <th></th>
                  {correlation.columns.map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {correlation.matrix.map((row, i) => (
                  <tr key={correlation.columns[i]}>
                    <th>{correlation.columns[i]}</th>
                    {row.map((v, j) => (
                      <td
                        key={j}
                        style={{
                          background: `rgba(79, 209, 197, ${Math.abs(v ?? 0) * 0.5})`,
                        }}
                      >
                        {v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
