"""Alpha feature definitions for Week 5 stock prediction."""

from __future__ import annotations

import math


def sign(value: float) -> int:
    """Return -1, 0, or 1 based on input sign."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def volume_confirmation(current_volume: float, volume_sma20: float, min_ratio: float = 1.1) -> bool:
    """Confirm momentum signal only when volume exceeds baseline by ratio."""
    if volume_sma20 <= 0:
        return False
    return (current_volume / volume_sma20) >= min_ratio


def alpha_sam(
    close_t: float,
    sma20: float,
    sentiment_t: float,
    current_volume: float,
    volume_sma20: float,
    min_volume_ratio: float = 1.1,
) -> float:
    """Sentiment-adjusted momentum with sign(s_t) and volume confirmation.

    alpha_sam = ((C_t - SMA20) / SMA20) * sign(S_t) * log(1 + |S_t|)
    If volume confirmation fails, alpha_sam returns 0.0.
    """
    if sma20 <= 0:
        raise ValueError("sma20 must be positive.")

    if not volume_confirmation(current_volume, volume_sma20, min_ratio=min_volume_ratio):
        return 0.0

    momentum = (close_t - sma20) / sma20
    sentiment_term = sign(sentiment_t) * math.log(1.0 + abs(sentiment_t))
    return momentum * sentiment_term
