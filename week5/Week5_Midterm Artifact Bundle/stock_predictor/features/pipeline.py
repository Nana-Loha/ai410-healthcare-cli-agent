"""Feature engineering pipeline for technical indicators and alpha computation."""

from __future__ import annotations

from dataclasses import dataclass

from ..features.alpha import alpha_sam, sign, volume_confirmation
from ..schemas import OHLCVBar, FeatureRow
from datetime import datetime


@dataclass(frozen=True)
class TechnicalIndicators:
    """Computed technical indicators for a symbol."""

    rsi14: float
    macd_line: float
    bb_width: float
    sma7: float
    sma20: float
    sma50: float


def compute_sma(prices: list[float], period: int) -> float | None:
    """Compute simple moving average."""
    if len(prices) < period or period <= 0:
        return None
    return sum(prices[-period:]) / period


def compute_rsi(prices: list[float], period: int = 14) -> float | None:
    """Compute Relative Strength Index."""
    if len(prices) < period + 1:
        return None

    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def compute_macd(prices: list[float]) -> float | None:
    """Compute MACD line (simplified: EMA12 - EMA26)."""
    if len(prices) < 26:
        return None

    ema12 = _ema(prices, 12)
    ema26 = _ema(prices, 26)

    if ema12 is None or ema26 is None:
        return None

    return ema12 - ema26


def _ema(prices: list[float], period: int) -> float | None:
    """Compute exponential moving average."""
    if len(prices) < period:
        return None
    multiplier = 2.0 / (period + 1)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = price * multiplier + ema * (1 - multiplier)
    return ema


def compute_bollinger_width(prices: list[float], period: int = 20) -> float | None:
    """Compute Bollinger Band width."""
    if len(prices) < period:
        return None

    sma = sum(prices[-period:]) / period
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std_dev = variance ** 0.5
    bb_width = 2 * std_dev
    return bb_width


def compute_technical_indicators(bars: list[OHLCVBar]) -> TechnicalIndicators | None:
    """Compute all technical indicators from OHLCV bars."""
    if not bars or len(bars) < 50:
        return None

    closes = [bar.close for bar in bars]

    rsi14 = compute_rsi(closes, period=14) or 50.0
    macd = compute_macd(closes) or 0.0
    bb_width = compute_bollinger_width(closes, period=20) or 0.0
    sma7 = compute_sma(closes, 7) or closes[-1]
    sma20 = compute_sma(closes, 20) or closes[-1]
    sma50 = compute_sma(closes, 50) or closes[-1]

    return TechnicalIndicators(
        rsi14=rsi14,
        macd_line=macd,
        bb_width=bb_width,
        sma7=sma7,
        sma20=sma20,
        sma50=sma50,
    )


def build_feature_row(
    symbol: str,
    timestamp: datetime,
    bars: list[OHLCVBar],
    sentiment_polarity: float,
    sentiment_momentum: float,
    sentiment_attention_score: float,
    sentiment_industry_relative: float,
) -> FeatureRow | None:
    """Build complete feature row with technical and sentiment features."""
    indicators = compute_technical_indicators(bars)
    if indicators is None or len(bars) < 1:
        return None

    latest_bar = bars[-1]
    sma20 = indicators.sma20

    # Compute alpha_SAM
    alpha_sam_value = alpha_sam(
        close_t=latest_bar.close,
        sma20=sma20,
        sentiment_t=sentiment_polarity,
        current_volume=float(latest_bar.volume),
        volume_sma20=200000.0,  # placeholder; use real volume SMA in production
        min_volume_ratio=1.1,
    )

    volume_ratio = latest_bar.volume / 200000.0 if latest_bar.volume > 0 else 0.0

    return FeatureRow(
        symbol=symbol,
        timestamp=timestamp,
        technical_rsi14=indicators.rsi14,
        technical_macd_line=indicators.macd_line,
        technical_bb_width=indicators.bb_width,
        technical_sma7=indicators.sma7,
        technical_sma20=indicators.sma20,
        technical_sma50=indicators.sma50,
        sentiment_polarity=sentiment_polarity,
        sentiment_momentum=sentiment_momentum,
        sentiment_attention_score=sentiment_attention_score,
        sentiment_industry_relative=sentiment_industry_relative,
        alpha_sam=alpha_sam_value,
        volume_ratio=volume_ratio,
    )
