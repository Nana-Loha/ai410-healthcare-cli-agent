"""Headline and X/Twitter cashtag adapters with provenance tracking."""

from __future__ import annotations

import re
from datetime import datetime

from ..schemas import HeadlineMessage


# Regex to extract cashtags like $AAPL, $TSLA from text
CASHTAG_PATTERN = re.compile(r"\$([A-Z]{1,5})\b")


def normalize_headline(
    symbol: str,
    text: str,
    timestamp: datetime,
    source: str,
    url: str | None = None,
) -> HeadlineMessage | None:
    """Normalize headline into canonical form.

    Validates:
    - Symbol is uppercase and 1-10 chars.
    - Text is non-empty.
    - Source is non-empty.

    Returns None if validation fails.
    """
    symbol = symbol.upper().strip()
    if not symbol or len(symbol) > 10:
        return None

    text = text.strip()
    if not text or len(text) > 5000:
        return None

    source = source.strip()
    if not source:
        return None

    if url is not None:
        url = url.strip() or None

    return HeadlineMessage(
        symbol=symbol,
        text=text,
        timestamp=timestamp,
        source=source,
        url=url,
    )


def extract_cashtags(text: str) -> list[str]:
    """Extract cashtags from raw text and return as uppercase symbols."""
    matches = CASHTAG_PATTERN.findall(text)
    return list(set(matches))  # deduplicate


def normalize_twitter_message(
    raw_text: str,
    timestamp: datetime,
    source: str = "twitter",
) -> list[HeadlineMessage]:
    """Parse Twitter cashtag message and emit one HeadlineMessage per cashtag.

    Returns list of normalized messages (empty if no cashtags found).
    """
    cashtags = extract_cashtags(raw_text)
    messages: list[HeadlineMessage] = []

    for symbol in cashtags:
        msg = normalize_headline(
            symbol=symbol,
            text=raw_text,
            timestamp=timestamp,
            source=source,
        )
        if msg is not None:
            messages.append(msg)

    return messages


def make_headline_dedup_key(msg: HeadlineMessage) -> str:
    """Generate deterministic deduplication key for headline/social message."""
    # Use symbol, text hash, and source to detect duplicates across feeds
    text_hash = hash(msg.text) & 0xFFFFFFFF
    return f"{msg.symbol}:{msg.timestamp.isoformat()}:{msg.source}:{text_hash}"
