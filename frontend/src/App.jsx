import { useState, useEffect } from "react";
import Analyzer from "./components/Analyzer";
import History from "./components/History";
import Header from "./components/Header";
import "./styles/global.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("analyze");

  return (
    <div className="app">
      <div className="bg-grid" />
      <div className="bg-orb orb1" />
      <div className="bg-orb orb2" />
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-content">
        {activeTab === "analyze" ? <Analyzer /> : <History />}
      </main>
      <footer className="footer">
        <span>Veritas v2.0 · DistilBERT + TF-IDF Ensemble</span>
        <span className="dot">·</span>
        <span>Built for truth</span>
      </footer>
    </div>
  );
}
