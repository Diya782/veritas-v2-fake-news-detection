"""
/api/v1/analyze - Core fake news detection endpoint
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid
import time
import logging
from services.claim_detector import analyze_text_structure

from services.model_service import ModelService
from services.feature_service import FeatureService
from utils.storage import ResultStorage

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=10000, description="News article text or headline")
    title: Optional[str] = Field(None, max_length=500, description="Optional article title")
    url: Optional[str] = Field(None, description="Optional source URL")

    @field_validator("text")
    @classmethod
    def text_must_be_meaningful(cls, v):
        if len(v.split()) < 5:
            raise ValueError("Text must contain at least 5 words")
        return v.strip()


class SignalBreakdown(BaseModel):
    bert_confidence: float
    tfidf_confidence: float
    linguistic_score: float
    source_credibility: float
    sentiment_bias: float


class AnalyzeResponse(BaseModel):
    id: str
    verdict: str
    confidence: float
    label: str
    signals: SignalBreakdown
    top_features: list
    explanation: str
    processing_time_ms: float
    timestamp: str

    # 🔥 ADD THESE
    needs_verification: Optional[bool] = False
    note: Optional[str] = None
    structure: Optional[dict] = None

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze news text for authenticity using an ensemble of:
    - DistilBERT fine-tuned on LIAR + FakeNewsNet datasets
    - TF-IDF + Passive Aggressive Classifier (fast fallback)
    - Linguistic feature analysis (sensationalism, punctuation patterns)
    - Sentiment bias detection
    """
    start_time = time.time()
    result_id = str(uuid.uuid4())[:8]

    try:
        model_service = ModelService.get_instance()
        feature_service = FeatureService()

        # Full text for analysis (combine title + body if both present)
        full_text = f"{request.title}. {request.text}" if request.title else request.text

        structure = analyze_text_structure(full_text)

        # Run ensemble inference
        result = model_service.predict(full_text)
        linguistic_features = feature_service.extract_linguistic_features(full_text)
        linguistic_score = 1 - linguistic_features["sensationalism_score"]
        # Ensemble fusion: weighted average
        bert_w, tfidf_w, ling_w = 0.55, 0.30, 0.15
        ensemble_confidence = (
            bert_w * result["bert_confidence"] +
            tfidf_w * result["tfidf_confidence"] +
            ling_w * linguistic_score
        )

        # 🔥 ADD THIS BLOCK HERE
        uncertainty_keywords = ["but", "however", "may", "could", "might", "warn", "critics"]

        if any(word in full_text.lower() for word in uncertainty_keywords):
            ensemble_confidence -= 0.1

        # optional extra refinement
        if "experts" in full_text.lower() or "analysts" in full_text.lower():
            ensemble_confidence -= 0.05

        # keep within bounds
        ensemble_confidence = max(0.0, min(1.0, ensemble_confidence))

        # Determine verdict
        if ensemble_confidence >= 0.70:
            verdict = "REAL"
            label = "Likely Authentic"
        elif ensemble_confidence <= 0.35:
            verdict = "FAKE"
            label = "Likely Misinformation"
        else:
            verdict = "UNCERTAIN"
            label = "Needs Verification"

        # Generate natural language explanation
        explanation = _generate_explanation(verdict, ensemble_confidence, linguistic_features, result)

        processing_time = (time.time() - start_time) * 1000

        response = AnalyzeResponse(
            id=result_id,
            verdict=verdict,
            confidence=round(ensemble_confidence, 4),
            label=label,
            signals=SignalBreakdown(
                bert_confidence=round(result["bert_confidence"], 4),
                tfidf_confidence=round(result["tfidf_confidence"], 4),
                linguistic_score=round(1 - linguistic_features["sensationalism_score"], 4),
                source_credibility=0.5,
                sentiment_bias=round(linguistic_features["sentiment_bias"], 4),
            ),
    top_features=result.get("top_features", []),
    explanation=explanation,
    processing_time_ms=round(processing_time, 2),
    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),

    # 🔥 ADD THESE TWO LINES
    needs_verification=(ensemble_confidence < 0.75 or verdict == "UNCERTAIN"),
    note="Low model confidence — verification recommended" if ensemble_confidence < 0.75 else None,

    structure=structure,
)

        # Store result in background
        background_tasks.add_task(ResultStorage.save, result_id, response.model_dump(), request.model_dump())

        logger.info(f"[{result_id}] verdict={verdict} conf={ensemble_confidence:.3f} time={processing_time:.1f}ms")
        return response

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis pipeline failed")


def _generate_explanation(verdict: str, confidence: float, ling: dict, model_result: dict) -> str:
    pct = int(confidence * 100)

    if verdict == "REAL":
        base = f"Our ensemble model rates this content as {pct}% likely authentic."
        if ling.get("sensationalism_score", 0) < 0.2:
            base += " The language is measured and factual, consistent with credible reporting."
        return base
    elif verdict == "FAKE":
        base = f"This content shows strong misinformation signals ({100-pct}% confidence)."
        if ling.get("sensationalism_score", 0) > 0.6:
            base += " Highly sensational language and emotional manipulation patterns were detected."
        elif ling.get("excessive_caps", False):
            base += " Excessive capitalization and clickbait patterns are hallmarks of low-credibility content."
        return base
    else:
        return (
            f"The model is uncertain ({pct}% real likelihood). "
            "Consider cross-referencing with established news sources before sharing."
        )
