"""Quality and SLA gate definitions for Week 5."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataQualityGates:
    """Thresholds for data pipeline quality checks."""

    max_null_rate: float = 0.05  # 5% null tolerance
    max_stale_hours: int = 24  # data older than 24h is stale
    min_symbol_coverage_pct: float = 0.90  # 90% of target universe
    min_bot_pass_rate_pct: float = 0.75  # 75% of social events must pass filter


@dataclass(frozen=True)
class ModelQualityGates:
    """Thresholds for model quality checks."""

    min_accuracy_pct: float = 55.0  # >55% directional accuracy target
    min_f1_score: float = 0.50  # balanced precision/recall


@dataclass(frozen=True)
class ServingSLAGates:
    """SLA requirements for serving layer."""

    max_symbol_batch_size: int = 500
    max_latency_seconds: float = 60.0  # must score 500 symbols in 60s
    max_error_rate_pct: float = 0.0  # zero errors allowed


# Singleton instances for use throughout pipeline
DATA_QUALITY_GATES = DataQualityGates()
MODEL_QUALITY_GATES = ModelQualityGates()
SERVING_SLA_GATES = ServingSLAGates()
