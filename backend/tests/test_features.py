"""
Tests for linguistic feature extraction
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.feature_service import FeatureService

svc = FeatureService()


def test_sensationalism_high_for_fake():
    text = "SHOCKING SECRET!!! Government hiding TRUTH about vaccines!!! SHARE before DELETED!!!"
    feats = svc.extract_linguistic_features(text)
    assert feats["sensationalism_score"] > 0.3, "Expected high sensationalism"
    assert feats["excessive_caps"] is True


def test_sensationalism_low_for_real():
    text = "The Reserve Bank of India maintained interest rates following its quarterly review, citing stable inflation data."
    feats = svc.extract_linguistic_features(text)
    assert feats["sensationalism_score"] < 0.3, "Expected low sensationalism"
    assert feats["excessive_caps"] is False


def test_credibility_markers():
    text = "According to the study published in Nature, the data shows a 30% reduction in emissions."
    feats = svc.extract_linguistic_features(text)
    assert feats["credibility_score"] > 0.0


def test_word_count():
    text = "one two three four five six seven"
    feats = svc.extract_linguistic_features(text)
    assert feats["word_count"] == 7


def test_reading_level_range():
    text = "The quick brown fox jumps over the lazy dog. This is a simple sentence."
    feats = svc.extract_linguistic_features(text)
    assert 0 <= feats["reading_level"] <= 100
