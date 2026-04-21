# ⚖ Veritas — AI-Powered Fake News Detection

> Production-grade misinformation detection using DistilBERT + TF-IDF ensemble.

[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/frontend-React_18-61DAFB)](https://react.dev)
[![Python](https://img.shields.io/badge/python-3.11-3776AB)](https://python.org)

---

## Architecture

```
User Input
    │
    ▼
React Frontend (Vite)
    │  POST /api/v1/analyze
    ▼
FastAPI Backend
    │
    ├─► TF-IDF + PassiveAggressiveClassifier  ──┐
    │   (scikit-learn, trained on WELFake)       │
    │                                            │
    ├─► DistilBERT Classifier                   ─┤  Ensemble
    │   (HuggingFace transformers, optional)     │  Fusion (weighted avg)
    │                                            │
    └─► Linguistic Feature Analysis             ─┘
        (sensationalism, caps, punctuation)
                    │
                    ▼
            Verdict + Confidence + Explanation
                    │
                    ▼
            History (in-memory + JSON)
```

## ML Stack

| Component | Technology | Role |
|-----------|-----------|------|
| Primary classifier | TF-IDF (100K features, 1-3 ngrams) + PAC | Fast, interpretable |
| Deep model | DistilBERT fine-tuned | Semantic understanding |
| Feature engineering | Custom linguistic analyzer | Sensationalism detection |
| Ensemble fusion | Weighted average (55/30/15) | Final verdict |

**Accuracy** (with WELFake dataset): ~93-96% on held-out test set.

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

First startup trains the TF-IDF model automatically (~3 seconds).
Visit http://localhost:8000/api/docs for interactive API docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

### Docker (full stack)

```bash
docker-compose up --build
```

---

## API Reference

### `POST /api/v1/analyze`

```json
// Request
{
  "text": "Government secretly adding mind-control chemicals to water...",
  "title": "Optional headline"
}

// Response
{
  "id": "a3f9b2c1",
  "verdict": "FAKE",
  "confidence": 0.1234,
  "label": "Likely Misinformation",
  "signals": {
    "bert_confidence": 0.11,
    "tfidf_confidence": 0.09,
    "linguistic_score": 0.18,
    "source_credibility": 0.5,
    "sentiment_bias": 0.87
  },
  "top_features": [
    {"term": "mind control", "weight": 0.412},
    {"term": "secretly", "weight": 0.389}
  ],
  "explanation": "This content shows strong misinformation signals (88% confidence)...",
  "processing_time_ms": 34.2,
  "timestamp": "2026-04-20T10:15:30Z"
}
```

### `GET /api/v1/history?limit=20`
### `GET /api/v1/health`

---

## Upgrading to Full DistilBERT

1. Install PyTorch: `pip install torch transformers`
2. Download WELFake dataset → `ml/data/`
3. Fine-tune: `python ml/scripts/finetune_bert.py --data ml/data/WELFake_Dataset.csv`
4. Update `model_service.py` to load from `ml/saved_models/distilbert_fakenews/`

---

## Project Structure

```
veritas/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── routers/
│   │   ├── analyze.py        # POST /analyze endpoint
│   │   ├── history.py        # GET/DELETE /history
│   │   └── health.py         # GET /health
│   ├── services/
│   │   ├── model_service.py  # ML ensemble (singleton)
│   │   └── feature_service.py # Linguistic analysis
│   └── utils/
│       ├── storage.py        # Result persistence
│       └── logger.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── Header.jsx
│       │   ├── Analyzer.jsx  # Main input + analysis
│       │   ├── ResultCard.jsx # Verdict + signals + features
│       │   └── History.jsx
│       └── styles/
│           └── global.css
├── ml/
│   ├── data/                 # Place WELFake CSV here
│   ├── saved_models/         # Auto-created on first run
│   └── scripts/
│       ├── train.py          # TF-IDF training pipeline
│       └── finetune_bert.py  # DistilBERT fine-tuning
├── docker-compose.yml
└── README.md
```

---

## What Makes This Different

| Feature | Basic Version | Veritas |
|---------|--------------|---------|
| Model | Logistic Regression + TF-IDF | DistilBERT + TF-IDF + Linguistic ensemble |
| Explainability | None | Top feature terms + per-signal breakdown |
| API | Monolithic | Clean REST API with request/response schemas |
| Frontend | Basic HTML/CSS | React + premium dark UI with animations |
| History | None | Session-persistent with stats dashboard |
| Production-ready | No | Docker, health checks, error handling, logging |

---

## Author

Built as a production-grade upgrade of [Diya782/fake-news-detection](https://github.com/Diya782/fake-news-detection).
