import { useState, useEffect } from "react";
import "./History.css";

const VERDICT_COLORS = {
  REAL: "var(--real)",
  FAKE: "var(--fake)",
  UNCERTAIN: "var(--uncertain)",
};

function HistoryItem({ entry }) {
  const [expanded, setExpanded] = useState(false);
  const result = entry.result;
  const color = VERDICT_COLORS[result?.verdict] || "var(--text-muted)";

  return (
    <div className={`history-item ${expanded ? "expanded" : ""}`}>
      <button className="history-item-header" onClick={() => setExpanded(!expanded)}>
        <div className="hi-left">
          <span
            className="hi-verdict-dot"
            style={{ background: color, boxShadow: `0 0 6px ${color}` }}
          />
          <div className="hi-text">
            <span className="hi-label" style={{ color }}>
              {result?.label || "—"}
            </span>
            <span className="hi-preview">{entry.input_preview}</span>
          </div>
        </div>
        <div className="hi-right">
          <span className="hi-confidence" style={{ color }}>
            {Math.round((result?.confidence || 0) * 100)}%
          </span>
          <span className="hi-time">{entry.saved_at?.slice(11, 19)}</span>
          <span className={`hi-chevron ${expanded ? "open" : ""}`}>›</span>
        </div>
      </button>

      {expanded && (
        <div className="history-item-body">
          <p className="hi-explanation">{result?.explanation}</p>
          <div className="hi-signals">
            {result?.signals &&
              Object.entries(result.signals).map(([key, val]) => (
                <div key={key} className="hi-signal-pill">
                  <span>{key.replace(/_/g, " ")}</span>
                  <span style={{ color }}>{Math.round(val * 100)}%</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function fetchHistory() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/history?limit=50");
      if (!res.ok) throw new Error("Failed to fetch history");
      const data = await res.json();
      setHistory(data.results || []);
    } catch (e) {
      setError("Cannot connect to backend. Run the server first.");
    } finally {
      setLoading(false);
    }
  }

  async function clearHistory() {
    await fetch("http://localhost:8000/api/v1/history", { method: "DELETE" });
    setHistory([]);
  }

  useEffect(() => {
    fetchHistory();
  }, []);

  const realCount = history.filter((h) => h.result?.verdict === "REAL").length;
  const fakeCount = history.filter((h) => h.result?.verdict === "FAKE").length;
  const uncCount = history.filter((h) => h.result?.verdict === "UNCERTAIN").length;

  return (
    <div className="history-page">
      <div className="history-header fade-up">
        <div>
          <h2 className="display-heading history-title">Analysis History</h2>
          <p className="history-sub">Your recent Veritas analyses, stored locally this session.</p>
        </div>
        <div className="history-actions">
          <button className="btn-ghost" onClick={fetchHistory}>Refresh</button>
          {history.length > 0 && (
            <button className="btn-ghost danger" onClick={clearHistory}>Clear all</button>
          )}
        </div>
      </div>

      {/* Stats bar */}
      {history.length > 0 && (
        <div className="stats-bar card fade-up-delay-1">
          <div className="stat">
            <span className="stat-num">{history.length}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-num" style={{ color: "var(--real)" }}>{realCount}</span>
            <span className="stat-label">Real</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-num" style={{ color: "var(--fake)" }}>{fakeCount}</span>
            <span className="stat-label">Fake</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-num" style={{ color: "var(--uncertain)" }}>{uncCount}</span>
            <span className="stat-label">Uncertain</span>
          </div>

          {/* Mini bar chart */}
          <div className="stats-bar-chart">
            {history.length > 0 && (
              <>
                <div
                  className="bar-seg"
                  style={{
                    width: `${(realCount / history.length) * 100}%`,
                    background: "var(--real)",
                  }}
                  title={`Real: ${realCount}`}
                />
                <div
                  className="bar-seg"
                  style={{
                    width: `${(fakeCount / history.length) * 100}%`,
                    background: "var(--fake)",
                  }}
                  title={`Fake: ${fakeCount}`}
                />
                <div
                  className="bar-seg"
                  style={{
                    width: `${(uncCount / history.length) * 100}%`,
                    background: "var(--uncertain)",
                  }}
                  title={`Uncertain: ${uncCount}`}
                />
              </>
            )}
          </div>
        </div>
      )}

      {/* List */}
      <div className="history-list fade-up-delay-2">
        {loading && (
          <div className="history-state">
            <div className="loading-dots">
              <span /><span /><span />
            </div>
            <p>Loading history…</p>
          </div>
        )}

        {!loading && error && (
          <div className="history-state error">
            <span className="state-icon">⚠</span>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && history.length === 0 && (
          <div className="history-state empty">
            <span className="state-icon">📭</span>
            <p>No analyses yet. Go to <strong>Analyze</strong> to get started.</p>
          </div>
        )}

        {!loading && !error && history.map((entry, i) => (
          <HistoryItem key={entry.id || i} entry={entry} />
        ))}
      </div>
    </div>
  );
}
