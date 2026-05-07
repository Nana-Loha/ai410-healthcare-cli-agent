"""Input validators for the healthcare CLI agent.

FR-004: no patient data is logged or persisted by any function here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class DosageValidationResult:
    valid: bool
    error: str | None = None


def validate_dosage(
    value: Union[int, float, str],
    min_mg: float = 0.001,
    max_mg: float = 10_000.0,
) -> DosageValidationResult:
    """Validate a medication dosage value.

    Checks that *value* is:
    1. Convertible to a finite float (numeric).
    2. Strictly positive (> 0).
    3. Within the inclusive safe range [min_mg, max_mg] in mg.

    Args:
        value:   Dosage to validate. Accepts int, float, or a numeric string.
        min_mg:  Inclusive lower bound in mg (default 0.001 mg).
        max_mg:  Inclusive upper bound in mg (default 10,000 mg / 10 g).

    Returns:
        DosageValidationResult(valid=True) on success, or
        DosageValidationResult(valid=False, error=<reason>) on failure.

    Example::

        >>> validate_dosage("500")
        DosageValidationResult(valid=True, error=None)

        >>> validate_dosage(-5)
        DosageValidationResult(valid=False, error='Dosage must be positive; got -5.0.')

        >>> validate_dosage("abc")
        DosageValidationResult(valid=False, error="Dosage must be numeric; got 'abc'.")

        # Narrow the range for a specific drug (e.g. warfarin 0.5–25 mg/day)
        >>> validate_dosage(50, min_mg=0.5, max_mg=25.0)
        DosageValidationResult(valid=False, error='Dosage 50.0 mg is outside the safe range [0.5, 25.0] mg.')
    """
    # 1. Numeric ---------------------------------------------------------------
    try:
        dose = float(value)
    except (TypeError, ValueError):
        return DosageValidationResult(
            valid=False,
            error=f"Dosage must be numeric; got {value!r}.",
        )

    if not math.isfinite(dose):
        return DosageValidationResult(
            valid=False,
            error=f"Dosage must be a finite number; got {dose}.",
        )

    # 2. Positive --------------------------------------------------------------
    if dose <= 0:
        return DosageValidationResult(
            valid=False,
            error=f"Dosage must be positive; got {dose}.",
        )

    # 3. Safe range ------------------------------------------------------------
    if not (min_mg <= dose <= max_mg):
        return DosageValidationResult(
            valid=False,
            error=(
                f"Dosage {dose} mg is outside the safe range "
                f"[{min_mg}, {max_mg}] mg."
            ),
        )

    return DosageValidationResult(valid=True)
