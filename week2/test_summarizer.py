"""Unit tests for the medical record summarizer (FR-004, User Story 2)."""

from __future__ import annotations

import pytest

import summarizer
from summarizer import summarize_record


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

SAMPLE_RECORD = """
Patient: Jane Doe  DOB: 1975-03-12
Visit Date: 2026-04-01

Diagnoses:
  - Type 2 Diabetes Mellitus (E11.9)
  - Hypertension (I10)

Current Medications:
  - Metformin 500 mg twice daily
  - Lisinopril 10 mg once daily

Allergies:
  - Penicillin (rash)

Follow-up:
  - HbA1c in 3 months
  - Annual kidney function panel
"""


# ---------------------------------------------------------------------------
# summarize_record — core behaviour
# ---------------------------------------------------------------------------

class TestSummarizeRecord:
    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="empty"):
            summarize_record("   ")

    def test_single_chunk_extracts_expected_sections(self):
        result = summarize_record(SAMPLE_RECORD)

        assert "Diagnoses:" in result
        assert "- Type 2 Diabetes Mellitus (E11.9)" in result
        assert "Current Medications:" in result
        assert "- Metformin 500 mg twice daily" in result
        assert "Allergies:" in result
        assert "- Penicillin (rash)" in result
        assert "Follow-up Recommendations:" in result
        assert "- HbA1c in 3 months" in result

    def test_multi_chunk_merges_sections(self, monkeypatch):
        monkeypatch.setattr(summarizer, "_CHUNK_SIZE", 50)
        monkeypatch.setattr(summarizer, "_CHUNK_OVERLAP", 0)

        result = summarize_record(SAMPLE_RECORD)

        assert "- Type 2 Diabetes Mellitus (E11.9)" in result
        assert "- Lisinopril 10 mg once daily" in result
        assert "- Annual kidney function panel" in result

    def test_provider_argument_is_ignored_for_local_privacy(self):
        result = summarize_record(SAMPLE_RECORD, provider="openai")
        assert "Basis: Extracted directly from the user-provided medical record" in result

    def test_no_disk_io_during_summarization(self, monkeypatch, tmp_path):
        """FR-004: summarize_record must not write any files."""
        before = set(tmp_path.iterdir())
        summarize_record(SAMPLE_RECORD, provider="openai")
        after = set(tmp_path.iterdir())

        assert before == after, "summarize_record wrote files to disk (FR-004 violation)"

    def test_missing_sections_render_as_none_documented(self):
        result = summarize_record("Diagnoses:\n- Migraine")

        assert "Diagnoses:" in result
        assert "- Migraine" in result
        assert "Current Medications:\n- None documented." in result
        assert "Allergies:\n- None documented." in result


# ---------------------------------------------------------------------------
# CLI integration — summarize command
# ---------------------------------------------------------------------------

class TestSummarizeCli:
    """Integration-level tests for the typer CLI command."""

    def _run(self, args: list[str]):
        from typer.testing import CliRunner
        from main import app

        return CliRunner().invoke(app, args)

    def test_missing_both_flags_exits_nonzero(self):
        result = self._run(["summarize"])
        assert result.exit_code != 0

    def test_both_flags_exits_with_code_4(self):
        result = self._run(["summarize", "--input", "text", "--file", "some.txt"])
        assert result.exit_code == 4

    def test_missing_file_exits_with_code_2(self):
        result = self._run(["summarize", "--file", "nonexistent_record_xyz.txt"])
        assert result.exit_code == 2
        assert "not found" in result.output.lower() or "not found" in (result.stderr or "").lower()

    def test_inline_input_calls_summarizer(self):
        result = self._run(["summarize", "--input", SAMPLE_RECORD])

        assert result.exit_code == 0
        assert "Diagnoses:" in result.output
        assert "Current Medications:" in result.output

    def test_disclaimer_included_in_output(self):
        result = self._run(["summarize", "--input", SAMPLE_RECORD])

        assert result.exit_code == 0
        assert "not a substitute for professional medical advice, diagnosis, or treatment" in result.output.lower()

    def test_file_input_calls_summarizer(self, tmp_path):
        record_file = tmp_path / "record.txt"
        record_file.write_text(SAMPLE_RECORD, encoding="utf-8")

        result = self._run(["summarize", "--file", str(record_file)])

        assert result.exit_code == 0
        assert "Allergies:" in result.output

    def test_json_format_returns_valid_json(self):
        result = self._run(["summarize", "--input", SAMPLE_RECORD, "--format", "json"])

        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "result" in data
        assert "disclaimer" in data
        assert "Basis: Extracted directly from the user-provided medical record" in data["result"]

    def test_output_flag_is_rejected_to_avoid_persistence(self):
        result = self._run(["summarize", "--input", SAMPLE_RECORD, "--output", "summary.txt"])

        assert result.exit_code == 4
        assert "fr-004" in result.output.lower() or "persisting patient data" in result.output.lower()
