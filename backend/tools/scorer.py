"""
Scoring logic for OER resources.

quality_score    — based on user ratings pulled from the source API (0–5)
accessibility_score — based on license openness / cost (0–5)
score_resource   — attaches both scores to a resource dict in place
"""

# Maps license keywords to an accessibility score (0–5).
# More permissive = higher score.
LICENSE_SCORES: list[tuple[str, float]] = [
    ("cc0", 5.0),
    ("public domain", 5.0),
    # More restrictive CC variants checked first so "cc by" doesn't match them early
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
    ("cc by", 5.0),           # plain CC BY — checked last among CC variants
    ("cc-by", 5.0),
    ("mit", 4.5),
    ("apache", 4.5),
    ("gpl", 4.0),
]

DEFAULT_ACCESSIBILITY = 2.0   # unknown license but passed the open-license gate
DEFAULT_QUALITY = 2.5         # no rating data available (neutral midpoint)


def accessibility_score(resource: dict) -> float:
    """Return a 0–5 score based on how open the resource's license is."""
    license_text = (resource.get("license") or resource.get("license_raw") or "").lower()
    for keyword, score in LICENSE_SCORES:
        if keyword in license_text:
            return score
    return DEFAULT_ACCESSIBILITY


def quality_score(resource: dict) -> float:
    """
    Return a 0–5 score based on user ratings.
    Expects optional fields: 'rating' (float 0–5) and 'review_count' (int).
    Falls back to DEFAULT_QUALITY when no rating data is present.
    """
    rating = resource.get("rating")
    review_count = resource.get("review_count", 0)

    if rating is None or review_count == 0:
        return DEFAULT_QUALITY

    # Bayesian-style shrinkage: blend the raw rating toward the default
    # so resources with very few reviews don't dominate.
    # With 10+ reviews the raw rating is weighted heavily.
    weight = min(review_count, 10) / 10
    return round(rating * weight + DEFAULT_QUALITY * (1 - weight), 2)


def score_resource(resource: dict) -> dict:
    """Attach quality_score, accessibility_score, and total_score to resource."""
    has_rating = resource.get("rating") is not None and resource.get("review_count", 0) > 0
    q = quality_score(resource)
    a = accessibility_score(resource)

    resource["has_rating"] = has_rating
    resource["quality_score"] = round(q, 2)
    resource["accessibility_score"] = round(a, 2)
    # Only factor quality into total when we have real rating data
    resource["total_score"] = round((q + a) / 2, 2) if has_rating else round(a, 2)
    return resource
