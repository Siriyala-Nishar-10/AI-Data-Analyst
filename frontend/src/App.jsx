import { useEffect, useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import OverviewTab from "./components/OverviewTab";
import DataTab from "./components/DataTab";
import ChartsTab from "./components/ChartsTab";
import ChatTab from "./components/ChatTab";
import {
  listDatasets,
  uploadDataset,
  deleteDataset,
  getPreview,
  getSummary,
} from "./api";
import "./App.css";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "data", label: "Data" },
  { id: "charts", label: "Charts" },
  { id: "chat", label: "Ask AI" },
];

const CHAT_STORAGE_KEY = "ai-data-analyst-chats";

export default function App() {
  const [datasets, setDatasets] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [tab, setTab] = useState("overview");

  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(null);

  const [summary, setSummary] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);
  const [listError, setListError] = useState(null);

  /*
   * Load chat conversations from localStorage
   * immediately when the component is created.
   *
   * Conversations are stored using dataset ID:
   *
   * {
   *   "2": [
   *     { role: "user", content: "..." },
   *     { role: "assistant", content: "..." }
   *   ]
   * }
   */
  const [chatMessages, setChatMessages] = useState(() => {
    try {
      const savedChats = localStorage.getItem(CHAT_STORAGE_KEY);

      if (!savedChats) {
        return {};
      }

      const parsedChats = JSON.parse(savedChats);

      if (
        parsedChats &&
        typeof parsedChats === "object" &&
        !Array.isArray(parsedChats)
      ) {
        return parsedChats;
      }

      return {};
    } catch (error) {
      console.error("Failed to load saved chats:", error);
      return {};
    }
  });

  /*
   * Save conversations whenever they change.
   */
  useEffect(() => {
    try {
      localStorage.setItem(
        CHAT_STORAGE_KEY,
        JSON.stringify(chatMessages)
      );
    } catch (error) {
      console.error("Failed to save chats:", error);
    }
  }, [chatMessages]);

  const refreshList = useCallback(async () => {
    try {
      const data = await listDatasets();

      setDatasets(data);
      setListError(null);

      return data;
    } catch (err) {
      setListError(err.message);
      return [];
    }
  }, []);

  useEffect(() => {
    refreshList().then((data) => {
      if (data.length > 0) {
        setSelectedId(data[0].id);
      }
    });
  }, [refreshList]);

  useEffect(() => {
    if (!selectedId) {
      setSummary(null);
      setPreview(null);
      return;
    }

    setLoadingDetail(true);
    setDetailError(null);

    Promise.all([
      getSummary(selectedId),
      getPreview(selectedId),
    ])
      .then(([s, p]) => {
        setSummary(s);
        setPreview(p);
      })
      .catch((err) => {
        setDetailError(err.message);
      })
      .finally(() => {
        setLoadingDetail(false);
      });
  }, [selectedId]);

  async function handleUpload(file) {
    setUploading(true);
    setUploadProgress(0);
    setUploadError(null);

    try {
      const dataset = await uploadDataset(
        file,
        setUploadProgress
      );

      await refreshList();

      setSelectedId(dataset.id);
      setTab("overview");
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteDataset(id);

      const remaining = await refreshList();

      /*
       * Also remove the deleted dataset's chat history.
       */
      setChatMessages((previous) => {
        const updated = { ...previous };
        delete updated[id];
        return updated;
      });

      if (selectedId === id) {
        setSelectedId(remaining[0]?.id ?? null);
      }
    } catch (err) {
      setListError(err.message);
    }
  }

  /*
   * Get conversation for the currently selected dataset.
   */
  function getChatMessages(datasetId) {
    return chatMessages[datasetId] || [];
  }

  /*
   * Update conversation for one dataset.
   */
  function handleChatMessagesChange(
    datasetId,
    messages
  ) {
    setChatMessages((previous) => ({
      ...previous,
      [datasetId]: messages,
    }));
  }

  /*
   * Clear conversation for one dataset.
   */
  function handleClearChat(datasetId) {
    setChatMessages((previous) => {
      const updated = { ...previous };

      delete updated[datasetId];

      return updated;
    });
  }

  const selectedDataset = datasets.find(
    (dataset) => dataset.id === selectedId
  );

  return (
    <div className="app-shell">
      <Sidebar
        datasets={datasets}
        selectedId={selectedId}
        onSelect={(id) => {
          setSelectedId(id);
          setTab("overview");
        }}
        onUpload={handleUpload}
        onDelete={handleDelete}
        uploading={uploading}
        uploadProgress={uploadProgress}
        uploadError={uploadError}
      />

      <main className="main-panel">
        {listError && (
          <div className="banner banner-error">
            {listError}
          </div>
        )}

        {!selectedDataset && (
          <div className="empty-state">
            <div className="empty-glyph">∴</div>

            <h2>No dataset selected</h2>

            <p>
              Upload a CSV file to view stats, charts, 
              and ask AI questions about your data.
            </p>
          </div>
        )}

        {selectedDataset && (
          <>
            <header className="content-header">
              <div>
                <h2>{selectedDataset.name}</h2>

                <p className="content-sub">
                  {selectedDataset.filename} &middot;
                  {" "}
                  uploaded{" "}
                  {new Date(
                    selectedDataset.uploaded_at
                  ).toLocaleString()}
                </p>
              </div>

              <div className="pulse-stats">
                <div className="pulse-stat">
                  <span className="pulse-value">
                    {selectedDataset.row_count ?? "—"}
                  </span>

                  <span className="pulse-label">
                    rows
                  </span>
                </div>

                <div
                  className="pulse-bars"
                  aria-hidden="true"
                >
                  {Array.from({ length: 12 }).map(
                    (_, i) => (
                      <span
                        key={i}
                        style={{
                          animationDelay: `${
                            i * 0.08
                          }s`,
                        }}
                      />
                    )
                  )}
                </div>

                <div className="pulse-stat">
                  <span className="pulse-value">
                    {selectedDataset.column_count ??
                      "—"}
                  </span>

                  <span className="pulse-label">
                    cols
                  </span>
                </div>
              </div>
            </header>

            <nav className="tab-row">
              {TABS.map((t) => (
                <button
                  key={t.id}
                  className={`tab-btn ${
                    tab === t.id
                      ? "tab-btn-active"
                      : ""
                  }`}
                  onClick={() => setTab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </nav>

            <div className="tab-content">
              {loadingDetail && (
                <p className="empty-hint">
                  Loading dataset…
                </p>
              )}

              {detailError && (
                <p className="upload-error">
                  {detailError}
                </p>
              )}

              {!loadingDetail && !detailError && (
                <>
                  {tab === "overview" && (
                    <OverviewTab summary={summary} />
                  )}

                  {tab === "data" && (
                    <DataTab preview={preview} />
                  )}

                  {tab === "charts" &&
                    summary && (
                      <ChartsTab
                        datasetId={selectedId}
                        columns={summary.columns}
                      />
                    )}

                  {tab === "chat" && (
                    <ChatTab
                      datasetId={selectedId}
                      datasetName={
                        selectedDataset.name
                      }
                      messages={getChatMessages(
                        selectedId
                      )}
                      onMessagesChange={(messages) =>
                        handleChatMessagesChange(
                          selectedId,
                          messages
                        )
                      }
                      onClearChat={() =>
                        handleClearChat(selectedId)
                      }
                    />
                  )}
                </>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}