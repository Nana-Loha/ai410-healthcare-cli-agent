"""Social stream filtering with bot detection and audit logging."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .ingestion import SocialMessage, filter_social_stream, BotFilterResult
from .headline_adapter import normalize_twitter_message, make_headline_dedup_key
from ..schemas import HeadlineMessage


class SocialStreamProcessor:
    """Process and filter social messages with audit trail."""

    def __init__(self, audit_log_path: str | None = None):
        """Initialize processor with optional audit log path."""
        self.audit_log_path = Path(audit_log_path) if audit_log_path else None
        self.audit_entries: list[dict] = []

    def process_twitter_message(
        self,
        raw_text: str,
        timestamp: datetime,
        account_age_days: int,
        posts_per_day: float,
        follower_following_ratio: float,
        duplicate_burst_count: int,
        contains_spam_link: bool = False,
    ) -> tuple[list[HeadlineMessage], list[BotFilterResult]]:
        """Process single Twitter message through bot filter and normalization.

        Returns:
        - List of kept HeadlineMessages (one per cashtag after filtering)
        - List of BotFilterResult decisions for each unique cashtag
        """
        # Extract cashtags and create social message objects
        messages_raw = normalize_twitter_message(raw_text, timestamp, source="twitter")
        kept_messages: list[HeadlineMessage] = []
        filter_results: list[BotFilterResult] = []

        for msg in messages_raw:
            social_msg = SocialMessage(
                symbol=msg.symbol,
                text=msg.text,
                account_age_days=account_age_days,
                posts_per_day=posts_per_day,
                follower_following_ratio=follower_following_ratio,
                duplicate_burst_count=duplicate_burst_count,
                contains_spam_link=contains_spam_link,
            )

            # Apply bot filter
            kept_list, filter_audit = filter_social_stream([social_msg])

            result = filter_audit[0]
            filter_results.append(result)

            if result.keep:
                kept_messages.append(msg)

            # Log audit entry
            self.audit_entries.append({
                "timestamp": timestamp.isoformat(),
                "symbol": msg.symbol,
                "source": "twitter",
                "bot_score": result.score,
                "bot_reasons": result.reasons,
                "kept": result.keep,
                "dedup_key": make_headline_dedup_key(msg),
            })

        return kept_messages, filter_results

    def flush_audit_log(self) -> None:
        """Write accumulated audit entries to log file."""
        if self.audit_log_path is None:
            return

        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, "w") as f:
            for entry in self.audit_entries:
                f.write(json.dumps(entry) + "\n")
