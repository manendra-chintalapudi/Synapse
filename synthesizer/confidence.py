"""Shared deterministic confidence calibration for evidence-backed Synapse views."""
from __future__ import annotations


def calibrate_confidence(
    *,
    direct_chain: bool,
    corroborating_sources: int = 0,
    sample_size: int = 1,
    authoritative_source: bool = False,
) -> dict:
    """Calibrate confidence from evidence shape and sample size, never model opinion."""
    corroborating_sources = max(0, int(corroborating_sources or 0))
    sample_size = max(0, int(sample_size or 0))
    if authoritative_source:
        level = "high"
        reason = "authoritative source directly supports the claim"
    elif direct_chain and corroborating_sources >= 2:
        level = "high"
        reason = f"direct evidence chain corroborated by {corroborating_sources} linked source types"
    elif direct_chain or corroborating_sources >= 1 or sample_size >= 3:
        level = "medium"
        reason = "direct evidence exists but corroboration or sample size is limited"
    else:
        level = "low"
        reason = "evidence is incomplete or indirect"
    return {
        "level": level,
        "reason": reason,
        "corroborating_sources": corroborating_sources,
        "sample_size": sample_size,
    }
