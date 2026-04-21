"""
FeatureService — Linguistic + stylometric feature extraction.

Signals extracted:
- Sensationalism score (caps, exclamation marks, clickbait phrases)
- Sentiment bias (extreme positive/negative = suspicious)
- Reading level (Flesch-Kincaid approximation)
- Excessive punctuation density
"""

import re
import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Clickbait / misinformation signal phrases
SENSATIONAL_PHRASES = [
    "you won't believe", "shocking", "breaking", "exposed", "secret",
    "they don't want you", "mainstream media", "wake up", "share before",
    "deleted", "banned", "hidden truth", "deep state", "illuminati",
    "miracle", "cure cancer", "doctors hate", "big pharma", "conspiracy",
    "leaked", "whistleblower", "urgent", "forward this", "exclusive",
    "bombshell", "stunning", "outrage", "scandalous", "unbelievable",
]

# Credibility markers found in real journalism
CREDIBILITY_MARKERS = [
    "according to", "confirmed by", "study published", "data shows",
    "research indicates", "official statement", "spokesperon said",
    "statistics show", "percent", "million", "billion", "report",
    "survey", "analysis", "peer-reviewed", "journal",
]


class FeatureService:
    def extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract all linguistic signals from text."""
        text_lower = text.lower()
        words = text.split()
        word_count = max(len(words), 1)
        char_count = max(len(text), 1)

        # 1. Sensationalism score
        caps_ratio = sum(1 for c in text if c.isupper()) / char_count
        exclamation_density = text.count("!") / word_count
        question_density = text.count("?") / word_count

        sensational_hits = sum(1 for phrase in SENSATIONAL_PHRASES if phrase in text_lower)
        sensational_phrase_score = min(sensational_hits / 5.0, 1.0)

        sensationalism_score = min(
            caps_ratio * 0.4 +
            exclamation_density * 0.3 +
            sensational_phrase_score * 0.3,
            1.0
        )

        # 2. Credibility markers
        credibility_hits = sum(1 for m in CREDIBILITY_MARKERS if m in text_lower)
        credibility_score = min(credibility_hits / 4.0, 1.0)

        # 3. Sentiment bias (simple heuristic — extreme emotion = suspicious)
        # Positive/negative word count ratio asymmetry
        positive_words = ["great", "amazing", "wonderful", "perfect", "success", "win"]
        negative_words = ["terrible", "disaster", "awful", "horrible", "worst", "fail"]
        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)
        total_sentiment = pos + neg
        if total_sentiment > 0:
            sentiment_bias = abs(pos - neg) / total_sentiment
        else:
            sentiment_bias = 0.0

        # 4. Reading level (simple approximation)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]
        avg_sentence_len = word_count / max(len(sentences), 1)
        avg_word_len = sum(len(w) for w in words) / word_count
        # Simple Flesch approximation
        flesch_score = max(0, min(100, 206.835 - 1.015 * avg_sentence_len - 84.6 * (avg_word_len / 5)))

        # 5. Excessive caps (all-caps words)
        caps_words = [w for w in words if len(w) > 3 and w.isupper()]
        excessive_caps = len(caps_words) > 3

        return {
            "sensationalism_score": round(sensationalism_score, 4),
            "credibility_score": round(credibility_score, 4),
            "sentiment_bias": round(sentiment_bias, 4),
            "caps_ratio": round(caps_ratio, 4),
            "exclamation_density": round(exclamation_density, 4),
            "reading_level": round(flesch_score, 1),
            "excessive_caps": excessive_caps,
            "word_count": word_count,
            "avg_sentence_len": round(avg_sentence_len, 1),
        }
