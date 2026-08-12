export default function DataTab({ preview }) {
  if (!preview) return null;
  const { columns, preview: rows, rows: totalRows } = preview;

  return (
    <div className="data-tab">
      <p className="section-label">
        Showing {rows.length} of {totalRows.toLocaleString()} rows
      </p>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={c}>{row[c] === null || row[c] === undefined ? "—" : String(row[c])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
