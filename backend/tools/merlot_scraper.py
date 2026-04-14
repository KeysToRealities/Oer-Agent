import requests

MERLOT_API_URL = "https://www.merlot.org/merlot/materials.rest"


def search_merlot(keywords: str) -> list[dict]:
    """
    Search MERLOT (Multimedia Educational Resource for Learning and Online Teaching)
    via their public REST API.
    """
    try:
        params = {
            "keywords": keywords,
            "page": 1,
            "pageSize": 25,
        }
        response = requests.get(
            MERLOT_API_URL,
            params=params,
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", {}).get("material", []):
            title = (item.get("title") or "").strip()
            url = item.get("URL") or item.get("url") or ""
            description = (item.get("description") or "").strip()
            license_raw = item.get("license") or item.get("creativeCommonsLicense") or ""
            material_type = item.get("materialType") or item.get("categoryType") or ""

            if not title or not url:
                continue

            results.append({
                "title": title,
                "url": url,
                "description": description,
                "license_raw": license_raw or "CC BY",
                "source": "MERLOT",
                "resource_type": material_type,
            })

        return results

    except Exception as e:
        print(f"[MERLOT] Error: {e}")
        return []
