"""Data ingestion contracts and X/Twitter cashtag bot filtering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SocialMessage:
    """Normalized social message used for sentiment feature generation."""

    symbol: str
    text: str
    account_age_days: int
    posts_per_day: float
    follower_following_ratio: float
    duplicate_burst_count: int
    contains_spam_link: bool = False


@dataclass(frozen=True)
class BotFilterResult:
    """Decision output from account/message heuristics."""

    keep: bool
    score: float
    reasons: tuple[str, ...]


def score_social_message(message: SocialMessage) -> BotFilterResult:
    """Score likely bot behavior using lightweight deterministic heuristics.

    Higher score indicates higher bot likelihood.
    """
    score = 0.0
    reasons: list[str] = []

    if message.account_age_days < 30:
        score += 1.0
        reasons.append("new_account")
    if message.posts_per_day > 50:
        score += 1.0
        reasons.append("high_post_velocity")
    if message.follower_following_ratio < 0.1:
        score += 0.5
        reasons.append("poor_follower_ratio")
    if message.duplicate_burst_count >= 3:
        score += 1.0
        reasons.append("duplicate_burst")
    if message.contains_spam_link:
        score += 1.0
        reasons.append("spam_link")

    return BotFilterResult(keep=score < 2.0, score=score, reasons=tuple(reasons))


def filter_social_stream(messages: list[SocialMessage]) -> tuple[list[SocialMessage], list[BotFilterResult]]:
    """Filter and annotate a stream of social cashtag messages."""
    kept: list[SocialMessage] = []
    audit: list[BotFilterResult] = []

    for msg in messages:
        result = score_social_message(msg)
        audit.append(result)
        if result.keep:
            kept.append(msg)
    return kept, audit
