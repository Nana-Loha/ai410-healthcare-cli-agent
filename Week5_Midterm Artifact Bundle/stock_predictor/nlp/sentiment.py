"""Sentiment model configuration for Week 5 implementation."""

from __future__ import annotations

SENTIMENT_MODEL_ID = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"


def get_sentiment_model_id() -> str:
    """Return the fixed sentiment model used by the Week 5 pipeline."""
    return SENTIMENT_MODEL_ID
