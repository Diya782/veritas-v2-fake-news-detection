import "./Header.css";

export default function Header({ activeTab, setActiveTab }) {
  return (
    <header className="header" role="banner">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon">⚖</span>
          <span className="logo-text">Veritas</span>
          <span className="logo-tag">AI</span>
        </div>

        <nav className="nav" role="navigation">
          <button
            className={`nav-btn ${activeTab === "analyze" ? "active" : ""}`}
            onClick={() => setActiveTab("analyze")}
          >
            Analyze
          </button>
          <button
            className={`nav-btn ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >
            History
          </button>
        </nav>

        <div className="header-badge">
          <span className="status-dot" />
          <span>Model live</span>
        </div>
      </div>
    </header>
  );
}
