"""Tests for feature pipeline, storage, and quality validation."""

from datetime import datetime, timedelta
import tempfile
from pathlib import Path

from Week5_midterm.stock_predictor.features.pipeline import (
    compute_sma,
    compute_rsi,
    compute_technical_indicators,
    build_feature_row,
)
from Week5_midterm.stock_predictor.features.store import (
    FeatureStore,
    generate_sample_ohlcv_bars,
)
from Week5_midterm.stock_predictor.features.quality import FeatureQualityValidator
from Week5_midterm.stock_predictor.schemas import OHLCVBar


def test_compute_sma() -> None:
    prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    sma3 = compute_sma(prices, 3)
    assert sma3 is not None
    assert abs(sma3 - 103.0) < 0.01  # (102 + 103 + 104) / 3


def test_compute_sma_insufficient_data() -> None:
    prices = [100.0, 101.0]
    sma5 = compute_sma(prices, 5)
    assert sma5 is None


def test_compute_rsi() -> None:
    prices = [100.0 + float(i) for i in range(30)]  # uptrend
    rsi = compute_rsi(prices, period=14)
    assert rsi is not None
    assert rsi > 50  # uptrend should give RSI > 50


def test_build_feature_row() -> None:
    ts = datetime(2026, 5, 12)
    bars = generate_sample_ohlcv_bars("AAPL", ts - timedelta(days=60), num_days=60)

    row = build_feature_row(
        symbol="AAPL",
        timestamp=bars[-1].timestamp,
        bars=bars,
        sentiment_polarity=0.5,
        sentiment_momentum=0.1,
        sentiment_attention_score=5.0,
        sentiment_industry_relative=0.05,
    )

    assert row is not None
    assert row.symbol == "AAPL"
    assert row.technical_sma20 > 0
    assert isinstance(row.alpha_sam, float)  # alpha_sam is computed (may be positive or negative)


def test_feature_store_roundtrip() -> None:
    ts = datetime(2026, 5, 12)
    bars = generate_sample_ohlcv_bars("AAPL", ts - timedelta(days=60), num_days=60)

    row = build_feature_row(
        symbol="AAPL",
        timestamp=bars[-1].timestamp,
        bars=bars,
        sentiment_polarity=0.3,
        sentiment_momentum=0.05,
        sentiment_attention_score=3.0,
        sentiment_industry_relative=0.02,
    )
    assert row is not None

    with tempfile.TemporaryDirectory() as tmpdir:
        store = FeatureStore(Path(tmpdir) / "features.csv")
        store.save_features([row])

        loaded = store.load_features()
        assert len(loaded) == 1
        assert loaded[0].symbol == "AAPL"
        assert abs(loaded[0].sentiment_polarity - 0.3) < 0.01


def test_quality_validator_pass() -> None:
    now = datetime.utcnow()
    ts = now - timedelta(days=60)  # historical price data
    bars = generate_sample_ohlcv_bars("AAPL", ts, num_days=60)

    row = build_feature_row(
        symbol="AAPL",
        timestamp=now,  # feature row has current timestamp
        bars=bars,
        sentiment_polarity=0.5,
        sentiment_momentum=0.1,
        sentiment_attention_score=5.0,
        sentiment_industry_relative=0.05,
    )
    assert row is not None

    validator = FeatureQualityValidator()
    report = validator.validate([row] * 500, now=now)

    # At least staleness should pass (fresh data)
    assert any(c.check_name == "staleness" and c.passed for c in report.checks)


def test_sample_ohlcv_generation() -> None:
    ts = datetime(2026, 5, 12)
    bars = generate_sample_ohlcv_bars("TSLA", ts, num_days=60)

    assert len(bars) == 60
    assert all(b.symbol == "TSLA" for b in bars)
    assert all(b.high >= b.low for b in bars)
    assert bars[0].timestamp == ts
    assert bars[-1].timestamp == ts + timedelta(days=59)
