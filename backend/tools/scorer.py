"""
Scoring logic for OER resources.

Five evaluation dimensions (each 0–5):
  open_license_score      — license permissiveness (heuristic lookup table)
  currency_score          — how current/up-to-date (Claude)
  pedagogical_value_score — educational quality (Claude)
  relevance_score         — relevance to the searched course (Claude)
  technical_quality_score — technical soundness (Claude)

quality_score is a bonus dimension when user-rating data is present (heuristic).
total_score is the mean of the five core dimensions (quality folds in when present).
"""

from services.claude_service import score_and_explain_resource

# Maps license keywords to an open-license score (0–5). More permissive = higher.
LICENSE_SCORES: list[tuple[str, float]] = [
    ("cc0", 5.0),
    ("public domain", 5.0),
    ("cc by-nc-nd", 2.5),
    ("cc-by-nc-nd", 2.5),
    ("cc by-nc-sa", 3.0),
    ("cc-by-nc-sa", 3.0),
    ("cc by-nc", 3.0),    ("cc-by-nc", 3.0),
    ("cc by-nd", 3.5),
    ("cc-by-nd", 3.5),
    ("cc by-sa", 4.5),
    ("cc-by-sa", 4.5),
    ("cc by", 5.0),
    ("cc-by", 5.0),
    ("mit", 4.5),
    ("apache", 4.5),
    ("gpl", 4.0),
]

DEFAULT_OPEN_LICENSE = 2.0

# Fallback values used when Claude is unavailable
_FALLBACK = {
    "currency_score": 3.0,
    "pedagogical_value_score": 3.0,
    "relevance_score": 2.5,
    "technical_quality_score": 3.0,
    "explanation": "",
}


def _is_free(resource: dict) -> int:
    """Return 1 if the resource is free, 0 if paid or unknown cost."""
    price = resource.get("purchase_price", "")
    if price:
        # Strip currency symbols and check if zero
        cleaned = price.replace("$", "").replace(",", "").strip()
        try:
            return 1 if float(cleaned) == 0.0 else 0
        except ValueError:
            pass
    # OER sources (ALG, OER Commons, LibreTexts, OpenStax) are always free
    free_sources = {"ALG", "OER Commons", "LibreTexts", "OpenStax", "Open Textbook Library"}
    if resource.get("source") in free_sources:
        return 1
    # CC-licensed resources are open access
    license_text = (resource.get("license") or resource.get("license_raw") or "").lower()
    if any(k in license_text for k in ("cc", "creative commons", "public domain", "cc0")):
        return 1
    return 0


def _open_license_score(resource: dict) -> float:
    """Deterministic lookup — license type fully determines this score."""
    license_text = (resource.get("license") or resource.get("license_raw") or "").lower()
    for keyword, score in LICENSE_SCORES:
        if keyword in license_text:
            return score
    return DEFAULT_OPEN_LICENSE



def _clamp(value, lo=0.0, hi=5.0) -> float:
    return round(max(lo, min(hi, float(value))), 2)


def score_resource(resource: dict, course: str = "") -> dict:
    """
    Attach all scoring dimensions to *resource* in place and return it.

    Claude evaluates four subjective dimensions and writes the explanation.
    Open-license score and user-rating quality score remain heuristic.
    """
    # limited_data = Claude only had a description to work from (no TOC, no structured content)
    has_toc = bool(resource.get("toc_labels"))
    has_description = bool((resource.get("full_description") or "").strip())
    limited_data = not has_toc and not has_description

    # --- Heuristic scores (no Claude needed) ---
    ol = _open_license_score(resource)

    # --- Claude scores (four dimensions + explanation) ---
    claude_out = score_and_explain_resource(resource, course)

    cu = _clamp(claude_out.get("currency_score",           _FALLBACK["currency_score"]))
    pv = _clamp(claude_out.get("pedagogical_value_score",  _FALLBACK["pedagogical_value_score"]))
    rv = _clamp(claude_out.get("relevance_score",          _FALLBACK["relevance_score"]))
    tq = _clamp(claude_out.get("technical_quality_score",  _FALLBACK["technical_quality_score"]))
    explanation = claude_out.get("explanation", "")

    resource["limited_data"]             = limited_data
    resource["is_free"]                  = _is_free(resource)
    resource["open_license_score"]       = round(ol, 2)
    resource["currency_score"]           = cu
    resource["pedagogical_value_score"]  = pv
    resource["relevance_score"]          = rv
    resource["technical_quality_score"]  = tq
    if explanation:
        resource["explanation"] = explanation

    resource["total_score"] = round(sum([ol, cu, pv, rv, tq]) / 5, 2)

    return resource
