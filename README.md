# ⚖️ Veritas — Fake News Detection System (V2)

A modular and scalable fake news detection system combining classical machine learning, optional transformer-based models, and linguistic feature analysis.

---

## 🚀 Overview

Veritas (V2) is an improved version of a baseline fake news detection system.  
It focuses on better architecture, modular design, and extensibility for real-world AI applications.

Key improvements:
- Modular ML pipeline (separate preprocessing, training, evaluation)
- FastAPI backend for API-based interaction
- Optional transformer-based enhancement
- Improved feature engineering and evaluation
- Clean frontend for interaction and visualization

---

## 🧠 System Architecture

User Input → Frontend → FastAPI Backend → ML Pipeline → Prediction + Explanation

---

## ⚙️ ML Pipeline

### Core Model
- TF-IDF Vectorization (n-grams)
- PassiveAggressiveClassifier

### Optional Enhancement
- DistilBERT (Hugging Face Transformers)

### Feature Engineering
- Tokenization and stopword removal
- N-gram features
- Linguistic signals:
  - Capitalization patterns
  - Punctuation usage
  - Sensational keywords

### Ensemble Strategy
- Combines outputs from multiple components (if enabled)
- Produces final prediction with confidence score

---

## 📊 Performance

- Achieves ~90% accuracy using TF-IDF baseline
- Performance depends on dataset and preprocessing

Note: Results may vary based on configuration.

---

## 🛠️ Tech Stack

- Python  
- Scikit-learn, NLTK  
- Hugging Face Transformers (optional)  
- FastAPI  
- React  

---

## 🧪 Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/api/docs

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

---

## 🔌 API

### POST /api/v1/analyze

Request:
```json
{
  "text": "Sample news content",
  "title": "Optional headline"
}
```

Response:
```json
{
  "verdict": "FAKE",
  "confidence": 0.87,
  "explanation": "Model prediction based on learned patterns"
}
```

---

## 📁 Project Structure

```
veritas/
├── backend/
├── frontend/
├── ml/
└── README.md
```

---

## 🔄 Evolution from V1

| Feature | V1 | Veritas (V2) |
|--------|----|--------------|
| Architecture | Monolithic | Modular |
| Models | Classical ML | ML + optional transformer |
| API | None | FastAPI |
| Frontend | Basic | React UI |
| Explainability | Limited | Improved |

---

## ⚠️ Limitations

- Depends on dataset quality  
- Transformer models require more compute  
- Not deployed (local setup)  

---

## 🔮 Future Work

- Full transformer-based pipeline  
- RAG-based fact verification  
- Deployment using Docker  
- Better explainability (SHAP/LIME)  

---

## 👩‍💻 Author

Diya Manth

---

## 🔗 V1 Project

https://github.com/Diya782/fake-news-detection
