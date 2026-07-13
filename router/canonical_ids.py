"""Shared canonical-ID candidate extraction for routing and evaluation.

This module intentionally handles explicit plant identifiers only. Resolution against the
locked ontology happens in the caller, so stale identifiers can be observed and rejected rather
than silently promoted to entities.
"""
from __future__ import annotations

import re


CANONICAL_ID_PATTERN = re.compile(
    r"(?<![A-Z0-9-])(?:"
    r"(?P<equipment>EQ-[A-Z0-9-]+)|"
    r"(?P<procedure>PROC-\d+)|"
    r"(?P<deviation>DEV\d+)|"
    r"(?P<rca>RCA\d+)|"
    r"(?P<raw_material>RM\d+)|"
    r"(?P<document>DOC\d+)|"
    r"(?P<quality_test>QT\d+)|"
    r"(?P<standard>STD-[A-Z0-9-]+)|"
    r"(?P<failure>F\d+)|"
    r"(?P<coil>C\d+)|"
    r"(?P<technician>T\d+)"
    r")(?![A-Z0-9-])",
    re.IGNORECASE,
)


def extract_id_candidates(text: str) -> list[dict]:
    """Return explicit ID candidates with type, normalized ID, surface text and offsets."""
    candidates = []
    for match in CANONICAL_ID_PATTERN.finditer(text or ""):
        candidates.append({
            "entity_type": match.lastgroup,
            "entity_id": match.group(0).upper(),
            "surface_text": match.group(0),
            "start_char": match.start(),
            "end_char": match.end(),
            "match_kind": "explicit_id",
        })
    return candidates


def unique_candidate_ids(text: str) -> set[str]:
    """Return the unique normalized identifiers observed in *text*."""
    return {candidate["entity_id"] for candidate in extract_id_candidates(text)}
