"""
ModelService — Singleton that manages:
  1. DistilBERT (fine-tuned for fake news classification)
     Uses: transformers + torch
  2. TF-IDF + PassiveAggressiveClassifier (fast, interpretable)
     Uses: scikit-learn

On first run, DistilBERT weights are downloaded from HuggingFace (free).
The TF-IDF model is trained locally using the bundled WELFake dataset subset.
"""

import os
import pickle
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "ml" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TFIDF_PATH = MODEL_DIR / "tfidf_pac.pkl"
BERT_AVAILABLE = False  # Set True when torch+transformers are installed

# ────────────────────────────────────────────────
# Try importing heavy ML deps; graceful fallback
# ────────────────────────────────────────────────
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    BERT_AVAILABLE = True
    logger.info("✅ torch + transformers available — DistilBERT mode enabled")
except ImportError:
    logger.warning("⚠️  torch/transformers not installed — running TF-IDF only mode")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import PassiveAggressiveClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.error("❌ scikit-learn not installed")


class ModelService:
    _instance: Optional["ModelService"] = None

    def __init__(self):
        self.models_ready = False
        self._bert_pipeline = None
        self._tfidf_vectorizer = None
        self._pac_classifier = None
        self._load_models()

    @classmethod
    def get_instance(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def _load_models(self):
        """Load or train all models."""
        logger.info("Loading ML models...")

        # 1. Load TF-IDF model (train if not cached)
        if SKLEARN_AVAILABLE:
            self._load_tfidf()

        # 2. Load DistilBERT (optional, requires torch)
        if BERT_AVAILABLE:
            self._load_bert()

        self.models_ready = True
        logger.info("✅ Models ready")

    def _load_tfidf(self):
        """Load or train TF-IDF + PAC pipeline."""
        if TFIDF_PATH.exists():
            logger.info("Loading cached TF-IDF model...")
            with open(TFIDF_PATH, "rb") as f:
                bundle = pickle.load(f)
                self._tfidf_vectorizer = bundle["vectorizer"]
                self._pac_classifier = bundle["classifier"]
            logger.info("✅ TF-IDF model loaded from cache")
        else:
            logger.info("Training TF-IDF model on built-in dataset...")
            self._train_tfidf()

    def _train_tfidf(self):
        """Train a TF-IDF + PassiveAggressiveClassifier from scratch using bundled data."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import PassiveAggressiveClassifier
        from sklearn.pipeline import Pipeline

        # Built-in training corpus (representative real/fake patterns)
        # In production: replace with WELFake / LIAR dataset CSVs
        train_texts, train_labels = self._get_builtin_corpus()

        self._tfidf_vectorizer = TfidfVectorizer(
            max_features=50000,
            ngram_range=(1, 3),
            sublinear_tf=True,
            min_df=2,
            strip_accents="unicode",
            analyzer="word",
            token_pattern=r"\w{1,}",
            stop_words="english",
        )
        self._pac_classifier = PassiveAggressiveClassifier(
            max_iter=1000,
            random_state=42,
            tol=1e-3,
            C=0.5,
        )

        X = self._tfidf_vectorizer.fit_transform(train_texts)
        self._pac_classifier.fit(X, train_labels)

        # Cache the trained model
        with open(TFIDF_PATH, "wb") as f:
            pickle.dump({
                "vectorizer": self._tfidf_vectorizer,
                "classifier": self._pac_classifier,
            }, f)
        logger.info(f"✅ TF-IDF model trained and cached → {TFIDF_PATH}")

    def _load_bert(self):
        """Load DistilBERT fine-tuned checkpoint from HuggingFace (free)."""
        try:
            # Using a publicly available fine-tuned fake news model
            model_name = "hamzab/roberta-fake-news-classifier"
            # For production: use "hamzab/roberta-fake-news-classifier" or fine-tune on LIAR
            logger.info(f"Loading DistilBERT: {model_name}")
            self._bert_pipeline = pipeline(
                "text-classification",
                model=model_name,
                truncation=True,
                max_length=512,
                device=-1,  # CPU; set to 0 for GPU
            )
            logger.info("✅ DistilBERT loaded")
        except Exception as e:
            logger.warning(f"DistilBERT load failed: {e} — falling back to TF-IDF only")
            self._bert_pipeline = None

    def predict(self, text: str) -> dict:
        """
        Run ensemble inference. Returns:
        {
          bert_confidence: float,   # probability of REAL
          tfidf_confidence: float,  # probability of REAL
          top_features: list,       # top TF-IDF n-grams
        }
        """
        result = {
            "bert_confidence": 0.5,
            "tfidf_confidence": 0.5,
            "top_features": [],
        }

        # TF-IDF prediction
        if self._tfidf_vectorizer and self._pac_classifier:
            try:
                X = self._tfidf_vectorizer.transform([text])
                # PAC gives decision function, not probability
                decision = self._pac_classifier.decision_function(X)[0]
                # Convert to 0–1 using sigmoid
                tfidf_conf = float(1 / (1 + np.exp(-decision)))
                result["tfidf_confidence"] = tfidf_conf

                # Extract top influential features
                feature_names = self._tfidf_vectorizer.get_feature_names_out()
                doc_tfidf = X.toarray()[0]
                top_idx = np.argsort(doc_tfidf)[-8:][::-1]
                result["top_features"] = [
                    {"term": feature_names[i], "weight": round(float(doc_tfidf[i]), 4)}
                    for i in top_idx if doc_tfidf[i] > 0
                ]
            except Exception as e:
                logger.error(f"TF-IDF inference error: {e}")

        # BERT prediction (if available)
        if self._bert_pipeline:
            try:
                truncated = text[:512]
                bert_result = self._bert_pipeline(truncated)[0]
                # SST-2 labels: POSITIVE = real-leaning, NEGATIVE = fake-leaning

                print("BERT OUTPUT:", bert_result)
                score = bert_result["score"]
                label = bert_result["label"].lower()

                if "real" in label or "true" in label:
                    result["bert_confidence"] = score
                else:
                    result["bert_confidence"] = 1 - score
            except Exception as e:
                logger.error(f"BERT inference error: {e}")
                result["bert_confidence"] = result["tfidf_confidence"]  # fallback
        else:
            result["bert_confidence"] = result["tfidf_confidence"]

        return result

    def _get_builtin_corpus(self):
        """
        Compact built-in corpus for initial model training.
        Replace or augment with WELFake/LIAR dataset in ml/data/ for full accuracy.
        Labels: 1 = real, 0 = fake
        """
        real = [
            "The Federal Reserve raised interest rates by 25 basis points on Wednesday, citing persistent inflation concerns.",
            "Scientists at CERN have detected a new particle consistent with theoretical predictions from the Standard Model.",
            "The Indian government announced a ₹2.5 lakh crore infrastructure budget for the next fiscal year.",
            "Apple reported quarterly earnings of $94.8 billion, beating analyst expectations by 3%.",
            "NASA's Perseverance rover has collected its 20th rock sample from the Jezero Crater on Mars.",
            "The World Health Organization confirmed a new strain of influenza has emerged in Southeast Asia.",
            "India's GDP grew at 7.2% in the last quarter, according to the Ministry of Statistics.",
            "Parliament passed the new data privacy bill with amendments after three days of debate.",
            "SpaceX successfully launched 60 Starlink satellites into low Earth orbit from Cape Canaveral.",
            "The Supreme Court upheld a lower court ruling on electoral bond transparency.",
            "Researchers published findings in Nature showing a link between sleep deprivation and cognitive decline.",
            "The Reserve Bank of India maintained the repo rate at 6.5% in its latest monetary policy meeting.",
            "ISRO's Gaganyaan mission is on track for a crewed launch in 2025, officials confirmed.",
            "The United Nations climate summit reached a new agreement on carbon emissions reduction targets.",
            "Microsoft announced quarterly revenue of $61.9 billion, with cloud services growing 21%.",
            "India's trade deficit narrowed to $19.1 billion in March, according to Commerce Ministry data.",
            "A new study in The Lancet found that regular exercise reduces dementia risk by 30%.",
            "The Election Commission announced polling dates for five state assemblies in November.",
            "Gold prices rose to ₹74,500 per 10 grams following global safe-haven demand.",
            "The Bombay High Court granted bail in the corruption case pending further investigation.",
        ]
        fake = [
            "SHOCKING: Government secretly putting mind-control chips in COVID vaccines EXPOSED!!!",
            "Scientists CONFIRM aliens landed in Delhi last night and met with government officials.",
            "You won't BELIEVE what they found in tap water — Big Pharma is hiding this CURE.",
            "BREAKING: Famous Bollywood actress arrested for running international drug cartel!!",
            "The moon landing was staged in a Hollywood studio, leaked NASA documents PROVE IT.",
            "Eating bleach cures cancer — doctors don't want you to know this ancient SECRET.",
            "URGENT FORWARD: WhatsApp will start charging ₹500/month unless you share this message.",
            "Illuminati confirmed: secret society running India's elections from underground bunker.",
            "5G towers are injecting radiation to depopulate cities — whistleblower REVEALS ALL.",
            "Bill Gates is microchipping children through school vaccines — exclusive leaked video.",
            "BREAKING: RBI to ban all cash and force digital payments within 48 HOURS!!!",
            "Ancient Indian scriptures prove Earth is only 6,000 years old — suppressed by scientists.",
            "Drinking cow urine CURES diabetes, doctors HATE this one weird trick from 1000 BC.",
            "Celebrity couple SECRETLY divorced — shocking truth the media WON'T tell you!!",
            "Government is adding fluoride to water to make citizens DUMB and obedient.",
            "EXPOSED: Mainstream media is all controlled by one secret billionaire family.",
            "This miracle berry DISSOLVES belly fat overnight — Bollywood stars' hidden weapon!",
            "FACT: Wearing magnets can protect you from 5G radiation — share before deleted!",
            "TOP SECRET: India is already at war and media is hiding CASUALTIES from public.",
            "Eating specific fruit in the morning REVERSES aging — Harvard BANNED this study!",
        ]
        texts = real + fake
        labels = [1] * len(real) + [0] * len(fake)
        return texts, labels
