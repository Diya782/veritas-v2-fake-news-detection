"""
backend/tests/test_analyze.py
Run with: pytest backend/tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_analyze_fake():
    response = client.post("/api/v1/analyze", json={
        "text": "SHOCKING: Government secretly putting mind-control chips in vaccines!!! SHARE BEFORE DELETED!!!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["FAKE", "UNCERTAIN", "REAL"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "signals" in data
    assert "explanation" in data
    assert "top_features" in data


def test_analyze_real():
    response = client.post("/api/v1/analyze", json={
        "text": "The Reserve Bank of India held the repo rate at 6.5% during its latest monetary policy meeting, citing inflationary pressures.",
        "title": "RBI holds rates steady"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] in ["REAL", "UNCERTAIN", "FAKE"]
    assert data["processing_time_ms"] > 0


def test_analyze_too_short():
    response = client.post("/api/v1/analyze", json={"text": "short"})
    assert response.status_code == 422


def test_analyze_empty():
    response = client.post("/api/v1/analyze", json={"text": ""})
    assert response.status_code == 422


def test_history_empty_or_filled():
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_signal_keys():
    response = client.post("/api/v1/analyze", json={
        "text": "Scientists confirm new approach to renewable energy dramatically cuts costs according to a peer-reviewed study published in Nature."
    })
    data = response.json()
    signals = data["signals"]
    assert "bert_confidence" in signals
    assert "tfidf_confidence" in signals
    assert "linguistic_score" in signals
    assert "sentiment_bias" in signals
