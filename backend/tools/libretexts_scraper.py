import requests
from bs4 import BeautifulSoup

LIBRETEXTS_SEARCH_URL = "https://libretexts.org/search"


def search_libretexts(keywords: str) -> list[dict]:
    """Scrape LibreTexts for resources matching keywords (fallback source)."""
    try:
        params = {"q": keywords}
        response = requests.get(LIBRETEXTS_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        # TODO: update selectors after inspecting LibreTexts' actual HTML structure
        for card in soup.select(".search-result"):
            title_el = card.select_one(".search-result__title")
            link_el = card.select_one("a")
            desc_el = card.select_one(".search-result__description")

            if not title_el or not link_el:
                continue

            results.append({
                "title": title_el.get_text(strip=True),
                "url": link_el["href"],
                "description": desc_el.get_text(strip=True) if desc_el else "",
                "license_raw": "CC BY-NC-SA",  # LibreTexts default license
                "source": "LibreTexts",
            })

        return results

    except Exception as e:
        print(f"[LibreTexts] Error: {e}")
        return []
