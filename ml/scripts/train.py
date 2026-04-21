"""
ml/scripts/train.py
-------------------
Full ML training pipeline for Veritas.

Pipeline:
  1. Load WELFake dataset (or built-in corpus)
  2. Preprocess text
  3. Train TF-IDF + PassiveAggressiveClassifier
  4. Evaluate + print metrics
  5. Save model artifacts

Usage:
  python ml/scripts/train.py
  python ml/scripts/train.py --data ml/data/WELFake_Dataset.csv
"""

import argparse
import logging
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "saved_models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_welfake(path: str):
    """Load WELFake CSV dataset (Title + Text, label: 0=fake, 1=real)."""
    import pandas as pd
    logger.info(f"Loading dataset from {path}")
    df = pd.read_csv(path)
    df = df.dropna(subset=["text"])
    df["combined"] = df["title"].fillna("") + " " + df["text"].fillna("")
    logger.info(f"Loaded {len(df)} samples | Real: {(df['label']==1).sum()} | Fake: {(df['label']==0).sum()}")
    return df["combined"].tolist(), df["label"].tolist()


def preprocess(texts):
    """Basic cleaning: lowercase, strip extra whitespace."""
    import re
    cleaned = []
    for t in texts:
        t = t.lower()
        t = re.sub(r"http\S+", " ", t)      # remove URLs
        t = re.sub(r"[^a-z0-9\s]", " ", t) # remove special chars
        t = re.sub(r"\s+", " ", t).strip()
        cleaned.append(t)
    return cleaned


def train(texts, labels):
    """Train TF-IDF + PassiveAggressiveClassifier pipeline."""
    logger.info("Preprocessing text...")
    texts = preprocess(texts)

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.15, random_state=42, stratify=labels
    )
    logger.info(f"Train: {len(X_train)} | Test: {len(X_test)}")

    # Build pipeline
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=100000,
            ngram_range=(1, 3),
            sublinear_tf=True,
            min_df=2,
            analyzer="word",
            stop_words="english",
        )),
        ("clf", PassiveAggressiveClassifier(
            max_iter=1000,
            random_state=42,
            C=0.5,
            tol=1e-3,
        )),
    ])

    logger.info("Training model...")
    pipe.fit(X_train, y_train)

    # Evaluation
    y_pred = pipe.predict(X_test)
    logger.info("\n" + classification_report(y_test, y_pred, target_names=["Fake", "Real"]))

    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"Confusion Matrix:\n{cm}")

    # AUC-ROC using decision function
    decisions = pipe.decision_function(X_test)
    auc = roc_auc_score(y_test, decisions)
    logger.info(f"ROC-AUC: {auc:.4f}")

    # Save
    output_path = OUTPUT_DIR / "tfidf_pac.pkl"
    with open(output_path, "wb") as f:
        pickle.dump({
            "vectorizer": pipe.named_steps["tfidf"],
            "classifier": pipe.named_steps["clf"],
            "metrics": {
                "auc": auc,
                "test_accuracy": pipe.score(X_test, y_test),
            }
        }, f)
    logger.info(f"✅ Model saved → {output_path}")
    return pipe


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None, help="Path to WELFake CSV")
    args = parser.parse_args()

    if args.data:
        texts, labels = load_welfake(args.data)
    else:
        logger.warning("No dataset provided — using built-in demo corpus (small, for testing only)")
        logger.warning("Download WELFake dataset from Kaggle for production quality")
        # Use the same corpus as ModelService
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
        from services.model_service import ModelService
        ms = ModelService.__new__(ModelService)
        texts, labels = ms._get_builtin_corpus()

    train(texts, labels)
