import "./ResultCard.css";

const VERDICT_CONFIG = {
  REAL: {
    icon: "✓",
    color: "var(--real)",
    dim: "var(--real-dim)",
    border: "rgba(0,229,160,0.25)",
    glow: "var(--glow-real)",
    label: "Likely Authentic",
    emoji: "🟢",
  },
  FAKE: {
    icon: "✕",
    color: "var(--fake)",
    dim: "var(--fake-dim)",
    border: "rgba(255,71,87,0.25)",
    glow: "var(--glow-fake)",
    label: "Likely Misinformation",
    emoji: "🔴",
  },
  UNCERTAIN: {
    icon: "?",
    color: "var(--uncertain)",
    dim: "var(--uncertain-dim)",
    border: "rgba(255,165,2,0.25)",
    glow: "0 0 30px rgba(255,165,2,0.12)",
    label: "Needs Verification",
    emoji: "🟡",
  },
};

function SignalBar({ label, value, description }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 65 ? "var(--real)" : pct <= 35 ? "var(--fake)" : "var(--uncertain)";

  return (
    <div className="signal-row">
      <div className="signal-meta">
        <span className="signal-label">{label}</span>
        <span className="signal-value" style={{ color }}>
          {pct}%
        </span>
      </div>
      <div className="signal-track">
        <div
          className="signal-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      {description && (
        <span className="signal-desc">{description}</span>
      )}
    </div>
  );
}

function FeatureTag({ term, weight }) {
  const intensity = Math.min(weight * 3, 1);
  return (
    <span
      className="feature-tag"
      style={{ opacity: 0.5 + intensity * 0.5 }}
      title={`TF-IDF weight: ${weight}`}
    >
      {term}
    </span>
  );
}


import { useState } from "react";

export default function ResultCard({ result, inputText = "" }) {
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const cfg = VERDICT_CONFIG[result.verdict] || VERDICT_CONFIG.UNCERTAIN;
  const confPct = Math.round(result.confidence * 100);

  function copyResult() {
    const text = `Veritas Analysis\nVerdict: ${result.label}\nConfidence: ${confPct}%\n\n${result.explanation}`;
    navigator.clipboard.writeText(text).catch(() => {});
  }

  async function handleVerify() {
  setLoading(true);
  try {
    const res = await fetch("http://127.0.0.1:8000/api/v1/verify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: inputText }),
    });

    const data = await res.json();
    setVerificationResult(data);
  } catch (err) {
    console.error(err);
  }
  setLoading(false);
}

  return (
    <div
      className="result-card card"
      style={{
        borderColor: cfg.border,
        boxShadow: `${cfg.glow}, var(--shadow-card)`,
      }}
    >
      {/* Verdict Header */}
      <div className="verdict-header">
        <div className="verdict-left">
          <div
            className="verdict-icon"
            style={{ background: cfg.dim, color: cfg.color, border: `1.5px solid ${cfg.border}` }}
          >
            {cfg.icon}
          </div>
          <div>
            <div className="verdict-label" style={{ color: cfg.color }}>
              {result.label}
            </div>
            <div className="verdict-id">
              ID #{result.id} ·{" "}
              <span className="mono">{result.processing_time_ms}ms</span>
            </div>
          </div>
        </div>

        <div className="confidence-ring-wrap">
          <svg className="confidence-ring" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="26" className="ring-track" />
            <circle
              cx="32"
              cy="32"
              r="26"
              className="ring-fill"
              style={{
                stroke: cfg.color,
                strokeDashoffset: `${163 - (163 * confPct) / 100}px`,
              }}
            />
          </svg>
          <div className="confidence-label">
            <span className="confidence-pct" style={{ color: cfg.color }}>
              {confPct}
            </span>
            <span className="confidence-unit">%</span>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="explanation-box">
        <p>{result.explanation}</p>
      </div>

    {/* 🧠 CONTENT STRUCTURE ANALYSIS */}
{result.structure && (
  <div style={{ marginTop: "14px" }}>
    <h3 style={{ fontSize: "13px", marginBottom: "6px", opacity: 0.8 }}>
      Content Analysis
    </h3>

    <div style={{ fontSize: "12.5px", lineHeight: "1.6", opacity: 0.9 }}>
      <p>📌 Facts: {result.structure.breakdown.FACT}</p>
      <p>🗣 Claims: {result.structure.breakdown.CLAIM}</p>
      <p>💭 Opinions: {result.structure.breakdown.OPINION}</p>
      <p>📊 Data Points: {result.structure.breakdown.DATA}</p>
    </div>
  </div>
)}  

      {/* ✅ VERIFY BUTTON ONLY FOR UNCERTAIN */}
{result.verdict === "UNCERTAIN" && (
  <div style={{ marginTop: "12px" }}>
    <button
      onClick={handleVerify}
      style={{
        background: "var(--uncertain)",
        color: "#111",
        padding: "10px 14px",
        borderRadius: "8px",
        border: "none",
        cursor: "pointer",
        fontWeight: "500"
      }}
    >
      ⚠️ Verify with Real Sources
    </button>
  </div>
)}

{/* 🔄 LOADING */}
{loading && <p style={{ marginTop: "10px" }}>Verifying...</p>}

{/* ✅ RESULT DISPLAY */}
{verificationResult && (
  <div style={{ marginTop: "20px" }}>
    <h3>Verification Summary</h3>

    <p>
      <b>Status:</b> {verificationResult.verification_status}
    </p>
    <p>
      <b>Confidence:</b> {verificationResult.confidence}
    </p>

    {/* 🔥 Metrics */}
    <div>
      <p>Similarity: {verificationResult.metrics?.similarity}</p>
      <p>Credibility: {verificationResult.metrics?.credibility}</p>
      <p>Agreement: {verificationResult.metrics?.agreement}</p>
    </div>

    {/* 🔥 Explanation */}
    <ul>
      {verificationResult.explanation?.map((e, i) => (
        <li key={i}>{e}</li>
      ))}
    </ul>

    {/* 🔥 Sources */}
    <h4>Sources</h4>
    <ul>
      {verificationResult.sources?.map((s, i) => (
        <li key={i}>
          <a href={s.url} target="_blank" rel="noreferrer">
            {s.title}
          </a>
          <span style={{ marginLeft: "8px", fontSize: "12px" }}>
            ({s.domain})
          </span>
        </li>
      ))}
    </ul>
  </div>
)}

      <div className="result-body">
        {/* Signal Breakdown */}
        <section className="result-section">
          <h3 className="section-title">Signal Breakdown</h3>
          <div className="signals-list">
            <SignalBar
              label="BERT Classifier"
              value={result.signals.bert_confidence}
              description="Deep language model confidence"
            />
            <SignalBar
              label="TF-IDF Model"
              value={result.signals.tfidf_confidence}
              description="Pattern & vocabulary analysis"
            />
            <SignalBar
              label="Linguistic Quality"
              value={result.signals.linguistic_score}
              description="Writing style & credibility markers"
            />
            <SignalBar
              label="Sentiment Balance"
              value={1 - result.signals.sentiment_bias}
              description="Emotional neutrality score"
            />
          </div>
        </section>

        {/* Top Features */}
        {result.top_features && result.top_features.length > 0 && (
          <section className="result-section">
            <h3 className="section-title">Key Terms Detected</h3>
            <p className="section-sub">
              High-weight n-grams that influenced the TF-IDF classification
            </p>
            <div className="feature-tags">
              {result.top_features.map((f, i) => (
                <FeatureTag key={i} term={f.term} weight={f.weight} />
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Footer */}
      <div className="result-footer">
        <span className="result-ts">{result.timestamp}</span>
        <button className="copy-btn" onClick={copyResult}>
          Copy result
        </button>
      </div>
    </div>
  );
}
