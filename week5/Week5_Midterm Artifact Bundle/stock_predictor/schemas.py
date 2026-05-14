"""Data schemas and contracts for Week 5 stock prediction pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OHLCVBar:
    """Normalized OHLCV bar for a single symbol."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class HeadlineMessage:
    """Normalized financial headline for sentiment processing."""

    symbol: str
    text: str
    timestamp: datetime
    source: str
    url: str | None = None


@dataclass(frozen=True)
class FeatureRow:
    """Computed feature vector for model scoring."""

    symbol: str
    timestamp: datetime
    technical_rsi14: float
    technical_macd_line: float
    technical_bb_width: float
    technical_sma7: float
    technical_sma20: float
    technical_sma50: float
    sentiment_polarity: float
    sentiment_momentum: float
    sentiment_attention_score: float
    sentiment_industry_relative: float
    alpha_sam: float
    volume_ratio: float


@dataclass(frozen=True)
class ScoringResponse:
    """API response envelope for a single prediction."""

    symbol: str
    timestamp: datetime
    direction: str  # "UP", "DOWN", "NEUTRAL"
    probability: float  # [0.0, 1.0]
    confidence_tier: str  # "HIGH", "MEDIUM", "LOW", "NEUTRAL"
    model_version: str
    freshness_seconds: float
    top_features: list[tuple[str, float]]  # [(feature_name, contribution), ...]
