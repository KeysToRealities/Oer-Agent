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
    ("cc by-nc", 3.0),
    ("cc-by-nc", 3.0),
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
DEFAULT_QUALITY = 2.5

# Fallback values used when Claude is unavailable
_FALLBACK = {
    "currency_score": 3.0,
    "pedagogical_value_score": 3.0,
    "relevance_score": 2.5,
    "technical_quality_score": 3.0,
    "interactivity_score": 2.5,
    "explanation": "",
}


def _open_license_score(resource: dict) -> float:
    """Deterministic lookup — license type fully determines this score."""
    license_text = (resource.get("license") or resource.get("license_raw") or "").lower()
    for keyword, score in LICENSE_SCORES:
        if keyword in license_text:
            return score
    return DEFAULT_OPEN_LICENSE


def _quality_score(resource: dict) -> float:
    """Bayesian blend of user rating toward the default when review count is low."""
    rating = resource.get("rating")
    review_count = resource.get("review_count", 0)
    if rating is None or review_count == 0:
        return DEFAULT_QUALITY
    weight = min(review_count, 10) / 10
    return round(rating * weight + DEFAULT_QUALITY * (1 - weight), 2)


def _clamp(value, lo=0.0, hi=5.0) -> float:
    return round(max(lo, min(hi, float(value))), 2)


def score_resource(resource: dict, course: str = "") -> dict:
    """
    Attach all scoring dimensions to *resource* in place and return it.

    Claude evaluates four subjective dimensions and writes the explanation.
    Open-license score and user-rating quality score remain heuristic.
    """
    has_rating = resource.get("rating") is not None and resource.get("review_count", 0) > 0

    # --- Heuristic scores (no Claude needed) ---
    ol = _open_license_score(resource)
    q  = _quality_score(resource)

    # --- Claude scores (four dimensions + explanation) ---
    claude_out = score_and_explain_resource(resource, course)

    cu = _clamp(claude_out.get("currency_score",          _FALLBACK["currency_score"]))
    pv = _clamp(claude_out.get("pedagogical_value_score", _FALLBACK["pedagogical_value_score"]))
    rv = _clamp(claude_out.get("relevance_score",         _FALLBACK["relevance_score"]))
    tq = _clamp(claude_out.get("technical_quality_score", _FALLBACK["technical_quality_score"]))
    ia = _clamp(claude_out.get("interactivity_score",     _FALLBACK["interactivity_score"]))
    explanation = claude_out.get("explanation", "")

    resource["has_rating"]              = has_rating
    resource["quality_score"]           = round(q,  2)
    resource["open_license_score"]      = round(ol, 2)
    resource["currency_score"]          = cu
    resource["pedagogical_value_score"] = pv
    resource["relevance_score"]         = rv
    resource["technical_quality_score"] = tq
    resource["interactivity_score"]     = ia
    if explanation:
        resource["explanation"] = explanation

    # license is display-only; relevance double-weighted so off-topic results sink
    core_scores = [cu, pv, rv, rv, tq, ia]
    if has_rating:
        core_scores.append(q)
    resource["total_score"] = round(sum(core_scores) / len(core_scores), 2)

    return resource
