"""Feature storage and reproducible sample dataset generation."""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

from ..schemas import FeatureRow, OHLCVBar


class FeatureStore:
    """Persist and load feature rows from CSV."""

    def __init__(self, path: str | Path):
        """Initialize feature store at given path."""
        self.path = Path(path)

    def save_features(self, rows: list[FeatureRow]) -> None:
        """Write feature rows to CSV file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "symbol",
                    "timestamp",
                    "technical_rsi14",
                    "technical_macd_line",
                    "technical_bb_width",
                    "technical_sma7",
                    "technical_sma20",
                    "technical_sma50",
                    "sentiment_polarity",
                    "sentiment_momentum",
                    "sentiment_attention_score",
                    "sentiment_industry_relative",
                    "alpha_sam",
                    "volume_ratio",
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    "symbol": row.symbol,
                    "timestamp": row.timestamp.isoformat(),
                    "technical_rsi14": row.technical_rsi14,
                    "technical_macd_line": row.technical_macd_line,
                    "technical_bb_width": row.technical_bb_width,
                    "technical_sma7": row.technical_sma7,
                    "technical_sma20": row.technical_sma20,
                    "technical_sma50": row.technical_sma50,
                    "sentiment_polarity": row.sentiment_polarity,
                    "sentiment_momentum": row.sentiment_momentum,
                    "sentiment_attention_score": row.sentiment_attention_score,
                    "sentiment_industry_relative": row.sentiment_industry_relative,
                    "alpha_sam": row.alpha_sam,
                    "volume_ratio": row.volume_ratio,
                })

    def load_features(self) -> list[FeatureRow]:
        """Load feature rows from CSV file."""
        if not self.path.exists():
            return []

        rows: list[FeatureRow] = []
        with open(self.path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(FeatureRow(
                    symbol=row["symbol"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    technical_rsi14=float(row["technical_rsi14"]),
                    technical_macd_line=float(row["technical_macd_line"]),
                    technical_bb_width=float(row["technical_bb_width"]),
                    technical_sma7=float(row["technical_sma7"]),
                    technical_sma20=float(row["technical_sma20"]),
                    technical_sma50=float(row["technical_sma50"]),
                    sentiment_polarity=float(row["sentiment_polarity"]),
                    sentiment_momentum=float(row["sentiment_momentum"]),
                    sentiment_attention_score=float(row["sentiment_attention_score"]),
                    sentiment_industry_relative=float(row["sentiment_industry_relative"]),
                    alpha_sam=float(row["alpha_sam"]),
                    volume_ratio=float(row["volume_ratio"]),
                ))
        return rows


def generate_sample_ohlcv_bars(
    symbol: str,
    start_date: datetime,
    num_days: int = 60,
    base_price: float = 100.0,
) -> list[OHLCVBar]:
    """Generate deterministic sample OHLCV bars for testing and benchmarking.

    Returns 60 daily bars with realistic price movements.
    """
    bars: list[OHLCVBar] = []
    price = base_price

    for i in range(num_days):
        ts = start_date + timedelta(days=i)

        # Deterministic "random" movement based on symbol and day
        hash_val = hash(f"{symbol}:{i}") & 0xFFFFFFFF
        pct_move = (hash_val % 1000) / 10000.0 - 0.05  # -5% to +5%
        price = price * (1.0 + pct_move)

        open_ = price * 0.99
        close = price * 1.01
        high = max(open_, close) * 1.02
        low = min(open_, close) * 0.98
        volume = 1000000 + (hash_val % 500000)

        bars.append(OHLCVBar(
            symbol=symbol,
            timestamp=ts,
            open=open_,
            high=high,
            low=low,
            close=close,
            volume=int(volume),
        ))

    return bars
