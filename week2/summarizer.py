"""Medical record summarization using in-memory LlamaIndex processing.

FR-004 compliance: patient-supplied record content is processed entirely in
memory. This module does not log, persist, or transmit record data to external
services.
"""

from __future__ import annotations

import re
from collections import OrderedDict

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

_CHUNK_SIZE = 3000
_CHUNK_OVERLAP = 200

_SECTION_ORDER = (
    "Diagnoses",
    "Current Medications",
    "Allergies",
    "Follow-up Recommendations",
)

_SECTION_ALIASES = {
    "diagnoses": "Diagnoses",
    "diagnosis": "Diagnoses",
    "conditions": "Diagnoses",
    "problem list": "Diagnoses",
    "current medications": "Current Medications",
    "medications": "Current Medications",
    "meds": "Current Medications",
    "allergies": "Allergies",
    "allergy": "Allergies",
    "follow-up": "Follow-up Recommendations",
    "follow up": "Follow-up Recommendations",
    "plan": "Follow-up Recommendations",
    "recommendations": "Follow-up Recommendations",
    "next steps": "Follow-up Recommendations",
}

_HEADING_RE = re.compile(r"^\s*([A-Za-z][A-Za-z\- ]+):\s*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.*\S)\s*$")


def _new_sections() -> dict[str, OrderedDict[str, None]]:
    return {name: OrderedDict() for name in _SECTION_ORDER}


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _resolve_section(heading: str) -> str | None:
    key = _normalize_whitespace(heading).lower()
    return _SECTION_ALIASES.get(key)


def _add_item(sections: dict[str, OrderedDict[str, None]], section: str, item: str) -> None:
    normalized = _normalize_whitespace(item)
    if normalized:
        sections[section].setdefault(normalized, None)


def _extract_sections_from_text(
    text: str,
    active_section: str | None = None,
) -> tuple[dict[str, OrderedDict[str, None]], str | None]:
    sections = _new_sections()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_match = _HEADING_RE.match(raw_line)
        if heading_match:
            active_section = _resolve_section(heading_match.group(1))
            continue

        bullet_match = _BULLET_RE.match(raw_line)
        if bullet_match and active_section:
            _add_item(sections, active_section, bullet_match.group(1))
            continue

        lowered = line.lower()
        if active_section == "Current Medications" and any(
            token in lowered for token in ("mg", "mcg", "tablet", "capsule", "daily", "twice")
        ):
            _add_item(sections, active_section, line)
            continue

        if active_section:
            _add_item(sections, active_section, line)

    return sections, active_section


def _merge_sections(chunks: list[dict[str, OrderedDict[str, None]]]) -> dict[str, OrderedDict[str, None]]:
    merged = _new_sections()
    for chunk in chunks:
        for section in _SECTION_ORDER:
            for item in chunk[section].keys():
                merged[section].setdefault(item, None)
    return merged


def _format_summary(sections: dict[str, OrderedDict[str, None]]) -> str:
    lines: list[str] = []
    for section in _SECTION_ORDER:
        lines.append(f"{section}:")
        items = list(sections[section].keys())
        if items:
            lines.extend(f"- {item}" for item in items)
        else:
            lines.append("- None documented.")
        lines.append("")
    lines.append("Basis: Extracted directly from the user-provided medical record in the current session.")
    return "\n".join(lines)


def summarize_record(text: str, provider: str | None = None) -> str:
    """Summarize a medical record into four structured sections.

    LlamaIndex is used for in-memory document chunking. The optional provider
    argument is accepted for CLI compatibility but ignored so patient data is
    not sent to external services.
    """
    del provider

    if not text or not text.strip():
        raise ValueError("Medical record text must not be empty.")

    document = Document(text=text)
    splitter = SentenceSplitter(chunk_size=_CHUNK_SIZE, chunk_overlap=_CHUNK_OVERLAP)
    nodes = splitter.get_nodes_from_documents([document])
    chunk_sections: list[dict[str, OrderedDict[str, None]]] = []
    active_section: str | None = None
    for node in nodes:
        section_chunk, active_section = _extract_sections_from_text(
            node.get_content(),
            active_section=active_section,
        )
        chunk_sections.append(section_chunk)
    merged_sections = _merge_sections(chunk_sections)
    return _format_summary(merged_sections)
