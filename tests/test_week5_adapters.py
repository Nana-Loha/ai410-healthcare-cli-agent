"""Integration tests for OHLCV and headline adapters."""

from datetime import datetime

from Week5_midterm.stock_predictor.data.ohlcv_adapter import normalize_ohlcv, make_ohlcv_dedup_key
from Week5_midterm.stock_predictor.data.headline_adapter import (
    normalize_headline,
    extract_cashtags,
    normalize_twitter_message,
    make_headline_dedup_key,
)
from Week5_midterm.stock_predictor.data.social_processor import SocialStreamProcessor


def test_ohlcv_normalization_valid() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    bar = normalize_ohlcv("aapl", ts, 150.0, 152.0, 149.0, 151.0, 10000000)
    assert bar is not None
    assert bar.symbol == "AAPL"
    assert bar.close == 151.0


def test_ohlcv_normalization_rejects_invalid_symbol() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    bar = normalize_ohlcv("", ts, 150.0, 152.0, 149.0, 151.0, 10000000)
    assert bar is None


def test_ohlcv_normalization_rejects_high_lt_low() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    bar = normalize_ohlcv("AAPL", ts, 150.0, 148.0, 149.0, 151.0, 10000000)
    assert bar is None


def test_ohlcv_normalization_rejects_negative_values() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    bar = normalize_ohlcv("AAPL", ts, -150.0, 152.0, 149.0, 151.0, 10000000)
    assert bar is None


def test_ohlcv_dedup_key() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    bar1 = normalize_ohlcv("AAPL", ts, 150.0, 152.0, 149.0, 151.0, 10000000)
    bar2 = normalize_ohlcv("AAPL", ts, 150.0, 152.0, 149.0, 151.0, 10000000)
    assert bar1 is not None and bar2 is not None
    assert make_ohlcv_dedup_key(bar1) == make_ohlcv_dedup_key(bar2)


def test_headline_normalization_valid() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    msg = normalize_headline("aapl", "Apple earnings beat", ts, "reuters", "https://example.com")
    assert msg is not None
    assert msg.symbol == "AAPL"
    assert msg.source == "reuters"


def test_headline_normalization_rejects_empty_text() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    msg = normalize_headline("AAPL", "", ts, "reuters")
    assert msg is None


def test_headline_normalization_rejects_empty_source() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    msg = normalize_headline("AAPL", "Some news", ts, "")
    assert msg is None


def test_cashtag_extraction() -> None:
    text = "Apple and Google both beat earnings. $AAPL $GOOGL on fire!"
    tags = extract_cashtags(text)
    assert set(tags) == {"AAPL", "GOOGL"}


def test_twitter_message_parsing() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    text = "Bullish on $AAPL and $MSFT today"
    messages = normalize_twitter_message(text, ts, source="twitter")
    assert len(messages) == 2
    assert {m.symbol for m in messages} == {"AAPL", "MSFT"}
    for m in messages:
        assert m.source == "twitter"


def test_twitter_message_no_cashtags() -> None:
    ts = datetime(2026, 5, 12, 10, 0, 0)
    text = "Just another regular tweet with no stocks"
    messages = normalize_twitter_message(text, ts)
    assert len(messages) == 0


def test_social_stream_processor_with_bot_filter() -> None:
    processor = SocialStreamProcessor()
    ts = datetime(2026, 5, 12, 10, 0, 0)

    kept, results = processor.process_twitter_message(
        raw_text="$AAPL is great",
        timestamp=ts,
        account_age_days=200,
        posts_per_day=5,
        follower_following_ratio=1.5,
        duplicate_burst_count=0,
    )

    assert len(kept) == 1
    assert len(results) == 1
    assert results[0].keep is True
    assert len(processor.audit_entries) == 1
