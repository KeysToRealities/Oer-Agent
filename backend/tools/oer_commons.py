import requests

OER_API_URL = "https://www.oercommons.org/api/v1/resources"


def search_oer_commons(keywords: str) -> list[dict]:
    """Search OER Commons public API for matching resources."""
    try:
        params = {
            "q": keywords,
            "limit": 25,
            "format": "json",
        }
        response = requests.get(OER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", []):
            rating = item.get("rating") or item.get("avg_rating")
            review_count = item.get("review_count") or item.get("reviews_count") or 0
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "license_raw": item.get("license", ""),
                "source": "OER Commons",
                "rating": float(rating) if rating is not None else None,
                "review_count": int(review_count),
            })

        return results

    except Exception as e:
        print(f"[OER Commons] Error: {e}")
        return []
