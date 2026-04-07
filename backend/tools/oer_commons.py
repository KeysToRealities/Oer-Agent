import requests

OER_API_URL = "https://www.oercommons.org/api/v1/resources"


def search_oer_commons(keywords: str) -> list[dict]:
    """Search OER Commons public API for matching resources."""
    try:
        params = {
            "q": keywords,
            "limit": 10,
            "format": "json",
        }
        response = requests.get(OER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "license_raw": item.get("license", ""),
                "source": "OER Commons",
            })

        return results

    except Exception as e:
        print(f"[OER Commons] Error: {e}")
        return []
