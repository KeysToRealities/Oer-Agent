import requests

OPENSTAX_API_URL = "https://openstax.org/apps/cms/api/v2/pages/"


def search_openstax(keywords: str) -> list[dict]:
    """
    Search the OpenStax book catalog using the Wagtail CMS API.
    All OpenStax books are CC BY.
    """
    try:
        search_terms = keywords.replace(",", " ").strip()
        if not search_terms:
            return []

        params = {
            "type": "books.Book",
            "fields": "title",
            "search": search_terms,
            "limit": 50,
        }
        response = requests.get(OPENSTAX_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            title = item.get("title", "")
            meta = item.get("meta", {})
            url = meta.get("html_url", "")
            if not title or not url:
                continue

            results.append({
                "title": title,
                "url": url,
                "description": f"An open textbook covering {title}.",
                "license_raw": "CC BY",
                "source": "OpenStax",
                "resource_type": "Open Textbook",
            })

        return results

    except Exception as e:
        print(f"[OpenStax] Error: {e}")
        return []
