import { useState, useRef } from "react";
import ResultCard from "./ResultCard";
import "./Analyzer.css";

const EXAMPLE_TEXTS = [
  {
    label: "Real news",
    text: "The Reserve Bank of India held the repo rate steady at 6.5% during its latest Monetary Policy Committee meeting, citing the need to monitor global inflation trends before making further adjustments.",
  },
  {
    label: "Misinformation",
    text: "SHOCKING: Government secretly adding mind-control chemicals to drinking water — whistleblower EXPOSES the truth they don't want you to know! SHARE BEFORE DELETED!!!",
  },
  {
    label: "Uncertain",
    text: "Scientists claim a new treatment may dramatically reduce aging effects within five years, though the research has not yet been peer-reviewed.",
  },
];

export default function Analyzer() {
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;

  async function handleAnalyze() {
    if (text.trim().length < 20) {
      setError("Please enter at least 20 characters of news text.");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim(), title: title.trim() || undefined }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);

      // Scroll to result
      setTimeout(() => {
        document.getElementById("result-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (e) {
      if (e.message.includes("fetch")) {
        setError("Cannot connect to backend. Make sure the server is running on port 8000.");
      } else {
        setError(e.message);
      }
    } finally {
      setLoading(false);
    }
  }

  function loadExample(example) {
    setText(example.text);
    setTitle("");
    setResult(null);
    setError(null);
    textareaRef.current?.focus();
  }

  function handleClear() {
    setText("");
    setTitle("");
    setResult(null);
    setError(null);
  }

  return (
    <div className="analyzer">
      {/* Hero */}
      <div className="hero fade-up">
        <div className="hero-eyebrow">
          <span className="eyebrow-pill">DistilBERT + TF-IDF Ensemble</span>
        </div>
        <h1 className="hero-title display-heading">
          Is this news<br />
          <span className="hero-highlight">real or fake?</span>
        </h1>
        <p className="hero-sub">
          Paste any article, headline, or WhatsApp forward. Veritas runs it
          through a multi-model AI pipeline and returns a verdict in under a second.
        </p>
      </div>

      {/* Input Card */}
      <div className="card input-card fade-up-delay-1">
        {/* Optional title */}
        <div className="input-row">
          <label className="input-label" htmlFor="title-input">
            Article title <span className="optional">(optional)</span>
          </label>
          <input
            id="title-input"
            className="title-input"
            type="text"
            placeholder="e.g. Government announces new policy on water quality"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={500}
          />
        </div>

        {/* Main textarea */}
        <div className="textarea-wrapper">
          <label className="input-label" htmlFor="news-text">
            News text <span className="required">*</span>
          </label>
          <textarea
            id="news-text"
            ref={textareaRef}
            className="news-textarea"
            placeholder="Paste the news article, headline, social media post, or WhatsApp message here…"
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={10000}
            rows={7}
          />
          <div className="textarea-meta">
            <span className={wordCount > 0 ? "meta-active" : ""}>
              {wordCount} words
            </span>
            <span>{charCount}/10,000</span>
          </div>
        </div>

        {/* Examples */}
        <div className="examples-row">
          <span className="examples-label">Try an example:</span>
          <div className="examples-chips">
            {EXAMPLE_TEXTS.map((ex) => (
              <button
                key={ex.label}
                className="example-chip"
                onClick={() => loadExample(ex)}
              >
                {ex.label}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="error-banner" role="alert">
            <span>⚠</span> {error}
          </div>
        )}

        {/* Actions */}
        <div className="action-row">
          {(text || result) && (
            <button className="btn-ghost" onClick={handleClear}>
              Clear
            </button>
          )}
          <button
            className="btn-analyze"
            onClick={handleAnalyze}
            disabled={loading || text.trim().length < 20}
          >
            {loading ? (
              <span className="btn-loading">
                <span className="spinner" />
                Analyzing…
              </span>
            ) : (
              <>
                <span className="btn-icon">⚡</span>
                Analyze Text
              </>
            )}
          </button>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div id="result-section" className="fade-up">
          <ResultCard result={result} inputText={text} />
        </div>
      )}
    </div>
  );
}
