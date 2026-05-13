"""Feature quality validation against pipeline gates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..gates import DATA_QUALITY_GATES
from ..schemas import FeatureRow


@dataclass(frozen=True)
class QualityCheckResult:
    """Result of a single quality check."""

    check_name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class QualityReport:
    """Full quality validation report."""

    checks: list[QualityCheckResult]

    def all_passed(self) -> bool:
        """Return True if all checks passed."""
        return all(c.passed for c in self.checks)

    def failed_checks(self) -> list[QualityCheckResult]:
        """Return list of failed checks."""
        return [c for c in self.checks if not c.passed]


class FeatureQualityValidator:
    """Validate feature rows against data quality gates."""

    def __init__(self, gates=None):
        """Initialize with optional custom gates."""
        self.gates = gates or DATA_QUALITY_GATES

    def validate(
        self,
        features: list[FeatureRow],
        now: datetime | None = None,
    ) -> QualityReport:
        """Run full quality validation on feature set."""
        if now is None:
            now = datetime.utcnow()

        checks: list[QualityCheckResult] = []

        # Check 1: Null rate
        null_count = self._count_nulls(features)
        null_rate = null_count / (len(features) * 14) if features else 0  # 14 numeric fields
        null_check = null_rate <= self.gates.max_null_rate
        checks.append(QualityCheckResult(
            check_name="null_rate",
            passed=null_check,
            message=f"Null rate {null_rate:.2%} vs threshold {self.gates.max_null_rate:.2%}",
        ))

        # Check 2: Stale data
        if features:
            max_age_hours = max(
                (now - f.timestamp).total_seconds() / 3600
                for f in features
            )
            stale_check = max_age_hours <= self.gates.max_stale_hours
            checks.append(QualityCheckResult(
                check_name="staleness",
                passed=stale_check,
                message=f"Max age {max_age_hours:.1f}h vs threshold {self.gates.max_stale_hours}h",
            ))
        else:
            checks.append(QualityCheckResult(
                check_name="staleness",
                passed=False,
                message="No features to validate",
            ))

        # Check 3: Symbol coverage
        if features:
            unique_symbols = len(set(f.symbol for f in features))
            target_coverage = 500  # S&P 500
            coverage_pct = unique_symbols / target_coverage
            coverage_check = coverage_pct >= self.gates.min_symbol_coverage_pct
            checks.append(QualityCheckResult(
                check_name="symbol_coverage",
                passed=coverage_check,
                message=f"Coverage {coverage_pct:.1%} ({unique_symbols}/{target_coverage}) vs threshold {self.gates.min_symbol_coverage_pct:.1%}",
            ))
        else:
            checks.append(QualityCheckResult(
                check_name="symbol_coverage",
                passed=False,
                message="No features to validate",
            ))

        # Check 4: Alpha quality (non-zero alpha values indicate signal)
        if features:
            non_zero_alphas = sum(1 for f in features if f.alpha_sam != 0.0)
            alpha_quality_rate = non_zero_alphas / len(features)
            alpha_check = alpha_quality_rate >= self.gates.min_bot_pass_rate_pct
            checks.append(QualityCheckResult(
                check_name="alpha_signal_quality",
                passed=alpha_check,
                message=f"Non-zero alpha {alpha_quality_rate:.1%} vs threshold {self.gates.min_bot_pass_rate_pct:.1%}",
            ))
        else:
            checks.append(QualityCheckResult(
                check_name="alpha_signal_quality",
                passed=False,
                message="No features to validate",
            ))

        return QualityReport(checks=checks)

    def _count_nulls(self, features: list[FeatureRow]) -> int:
        """Count null-like values (0.0 for numeric fields)."""
        count = 0
        for f in features:
            # Note: 0.0 is technically valid for many fields, but used as null proxy
            # In production, use proper None checks
            numeric_fields = [
                f.technical_rsi14, f.technical_macd_line, f.technical_bb_width,
                f.technical_sma7, f.technical_sma20, f.technical_sma50,
                f.sentiment_polarity, f.sentiment_momentum,
                f.sentiment_attention_score, f.sentiment_industry_relative,
                f.alpha_sam, f.volume_ratio,
            ]
            count += sum(1 for v in numeric_fields if v == 0.0)
        return count
