import requests

ALG_BASE_URL = "https://alg.manifoldapp.org"
ALG_API_URL = f"{ALG_BASE_URL}/api/v1/projects"


def search_alg(keywords: str) -> list[dict]:
    """Search Affordable Learning Georgia via their JSON API."""
    try:
        params = {
            "filter[keyword]": keywords,
            "page[size]": 10,
        }
        response = requests.get(
            ALG_API_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            slug = attrs.get("slug", "")
            title = attrs.get("titlePlaintext", "").strip()
            description = attrs.get("subtitlePlaintext", "").strip()

            if not title:
                continue

            results.append({
                "title": title,
                "url": f"{ALG_BASE_URL}/projects/{slug}",
                "description": description,
                "license_raw": "CC BY",
                "source": "ALG",
            })

        return results

    except Exception as e:
        print(f"[ALG] Error: {e}")
        return []
