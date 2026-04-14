import requests

ALG_BASE_URL = "https://alg.manifoldapp.org"
ALG_API_URL = f"{ALG_BASE_URL}/api/v1/projects"

# Infer resource type from slug/title patterns
def _infer_type(slug: str, title: str) -> str:
    slug = slug.lower()
    title = title.lower()
    if slug.startswith("rg-") or "research grant" in title or "research report" in title:
        return "Research Grant"
    if "adoption" in slug or "adoption" in title:
        return "Adoption"
    if "ancillary" in slug or "ancillary" in title or "lab manual" in title:
        return "Ancillary Material"
    if "training" in slug or "training" in title:
        return "Training Resource"
    return "Open Textbook"


def _fetch_alg(query: str) -> list:
    params = {
        "filter[keyword]": query,
        "page[size]": 20,
    }
    response = requests.get(
        ALG_API_URL,
        params=params,
        headers={"Accept": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def search_alg(keywords: str) -> list[dict]:
    """Search Affordable Learning Georgia via their JSON API."""
    try:
        # Strip commas in case the keyword string was comma-separated
        keywords = keywords.replace(",", " ").strip()

        data = _fetch_alg(keywords)

        # If the full query returns few results, try each individual word
        # and keep whichever gives the most results
        if len(data) < 5 and " " in keywords:
            for word in keywords.split():
                candidate = _fetch_alg(word)
                if len(candidate) > len(data):
                    data = candidate

        results = []
        for item in data:
            attrs = item.get("attributes", {})
            slug = attrs.get("slug", "")
            title = attrs.get("titlePlaintext", "").strip()
            institution = attrs.get("subtitlePlaintext", "").strip()
            description = attrs.get("descriptionPlaintext", "").strip()
            creators = attrs.get("creatorNames", "").strip()

            if not title:
                continue

            # Build a readable description from available fields
            desc_parts = []
            if institution:
                desc_parts.append(institution)
            if creators:
                desc_parts.append(f"By {creators}")
            if description:
                desc_parts.append(description)

            results.append({
                "title": title,
                "url": f"{ALG_BASE_URL}/projects/{slug}",
                "description": " — ".join(desc_parts),
                "license_raw": "CC BY",
                "source": "ALG",
                "resource_type": _infer_type(slug, title),
            })

        return results

    except Exception as e:
        print(f"[ALG] Error: {e}")
        return []
