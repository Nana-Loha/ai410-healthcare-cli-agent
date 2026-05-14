"""OHLCV market data adapter with deterministic normalization."""

from __future__ import annotations

from datetime import datetime

from ..schemas import OHLCVBar


def normalize_ohlcv(
    symbol: str,
    timestamp: datetime,
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: int,
) -> OHLCVBar | None:
    """Normalize raw OHLCV row into canonical form.

    Validates:
    - Symbol is uppercase.
    - OHLC values are positive and high >= low.
    - Volume is non-negative.
    - No NaN or infinite values.

    Returns None if validation fails.
    """
    symbol = symbol.upper().strip()
    if not symbol or len(symbol) > 10:
        return None

    if not (open_ > 0 and high > 0 and low > 0 and close > 0):
        return None

    if not (high >= low):
        return None

    if volume < 0:
        return None

    for val in [open_, high, low, close]:
        if not (-1e10 < val < 1e10):  # catch NaN, inf
            return None

    return OHLCVBar(
        symbol=symbol,
        timestamp=timestamp,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def make_ohlcv_dedup_key(bar: OHLCVBar) -> str:
    """Generate deterministic deduplication key for OHLCV bar."""
    return f"{bar.symbol}:{bar.timestamp.isoformat()}"
