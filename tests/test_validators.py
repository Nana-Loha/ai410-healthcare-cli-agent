"""Tests for validators.validate_dosage."""

from __future__ import annotations

import math

import pytest

from validators import validate_dosage


class TestValidateDosageNumericCheck:
    def test_int_accepted(self):
        assert validate_dosage(500).valid is True

    def test_float_accepted(self):
        assert validate_dosage(0.25).valid is True

    def test_numeric_string_accepted(self):
        assert validate_dosage("250").valid is True

    def test_non_numeric_string_rejected(self):
        result = validate_dosage("abc")
        assert result.valid is False
        assert "numeric" in result.error.lower()

    def test_none_rejected(self):
        result = validate_dosage(None)
        assert result.valid is False

    def test_infinity_rejected(self):
        result = validate_dosage(math.inf)
        assert result.valid is False
        assert "finite" in result.error.lower()

    def test_nan_rejected(self):
        result = validate_dosage(math.nan)
        assert result.valid is False
        assert "finite" in result.error.lower()


class TestValidateDosagePositiveCheck:
    def test_zero_rejected(self):
        result = validate_dosage(0)
        assert result.valid is False
        assert "positive" in result.error.lower()

    def test_negative_rejected(self):
        result = validate_dosage(-1)
        assert result.valid is False
        assert "positive" in result.error.lower()

    def test_very_small_positive_accepted(self):
        # 0.001 mg is the default lower bound
        assert validate_dosage(0.001).valid is True


class TestValidateDosageSafeRange:
    def test_value_below_min_rejected(self):
        result = validate_dosage(0.0001)  # below default min 0.001
        assert result.valid is False
        assert "outside the safe range" in result.error.lower()

    def test_value_above_max_rejected(self):
        result = validate_dosage(10_001)  # above default max 10,000
        assert result.valid is False
        assert "outside the safe range" in result.error.lower()

    def test_value_at_min_boundary_accepted(self):
        assert validate_dosage(0.001).valid is True

    def test_value_at_max_boundary_accepted(self):
        assert validate_dosage(10_000).valid is True

    def test_custom_range_too_high(self):
        result = validate_dosage(50, min_mg=0.5, max_mg=25.0)
        assert result.valid is False
        assert "25.0" in result.error

    def test_custom_range_valid(self):
        assert validate_dosage(10, min_mg=0.5, max_mg=25.0).valid is True


class TestValidateDosageErrorMessages:
    def test_error_is_none_on_success(self):
        result = validate_dosage(100)
        assert result.error is None

    def test_error_contains_bad_value(self):
        result = validate_dosage("badval")
        assert "badval" in result.error

    def test_error_contains_range_bounds_for_range_violation(self):
        result = validate_dosage(99_999)
        assert "10000" in result.error or "10,000" in result.error
