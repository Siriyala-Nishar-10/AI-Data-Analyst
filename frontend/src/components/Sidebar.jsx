import { useRef, useState } from "react";
import { Trash2, UploadCloud, Database } from "lucide-react";

export default function Sidebar({
  datasets,
  selectedId,
  onSelect,
  onUpload,
  onDelete,
  uploading,
  uploadProgress,
  uploadError,
}) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  function handleFiles(files) {
    const file = files?.[0];

    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      return;
    }

    onUpload(file);
  }

  function openFilePicker() {
    if (!uploading) {
      inputRef.current?.click();
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand">
          <span className="brand-mark">AD</span>

          <div>
            <h1>AI Data Analyst</h1>
            <p className="brand-sub">
              explore &middot; visualize &middot; ask
            </p>
          </div>
        </div>
      </div>

      <div
        className={`dropzone ${
          dragOver ? "dropzone-active" : ""
        } ${uploading ? "dropzone-disabled" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!uploading) setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);

          if (!uploading) {
            handleFiles(e.dataTransfer.files);
          }
        }}
        role="region"
        aria-label="CSV upload area"
      >
        <UploadCloud size={20} strokeWidth={1.75} />

        <span>
          {uploading
            ? `Uploading… ${uploadProgress}%`
            : "Drop a CSV here"}
        </span>

        <button
          type="button"
          className="upload-button"
          onClick={openFilePicker}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Choose CSV"}
        </button>

        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => {
            handleFiles(e.target.files);

            // Allows selecting the same CSV again later.
            e.target.value = "";
          }}
          disabled={uploading}
          style={{
            position: "absolute",
            width: "1px",
            height: "1px",
            padding: 0,
            margin: "-1px",
            overflow: "hidden",
            clip: "rect(0, 0, 0, 0)",
            whiteSpace: "nowrap",
            border: 0,
          }}
        />
      </div>

      {uploadError && (
        <p className="upload-error">{uploadError}</p>
      )}

      <div className="dataset-list">
        <p className="section-label">
          Datasets ({datasets.length})
        </p>

        {datasets.length === 0 && (
          <p className="empty-hint">
            Upload a CSV to start analyzing.
          </p>
        )}

        {datasets.map((ds) => (
          <div
            key={ds.id}
            className={`dataset-item ${
              ds.id === selectedId
                ? "dataset-item-active"
                : ""
            }`}
            onClick={() => onSelect(ds.id)}
          >
            <Database
              size={15}
              strokeWidth={1.75}
              className="dataset-icon"
            />

            <div className="dataset-meta">
              <span className="dataset-name">
                {ds.name}
              </span>

              <span className="dataset-sub">
                {ds.row_count ?? "?"} rows &middot;{" "}
                {ds.column_count ?? "?"} cols
              </span>
            </div>

            <button
              type="button"
              className="icon-btn"
              title="Delete dataset"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(ds.id);
              }}
            >
              <Trash2
                size={14}
                strokeWidth={1.75}
              />
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}