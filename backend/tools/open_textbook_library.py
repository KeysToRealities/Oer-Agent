import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

OTL_SEARCH_URL = "https://open.umn.edu/opentextbooks/textbooks"
ATOM_NS = "http://www.w3.org/2005/Atom"


def search_open_textbook_library(keywords: str) -> list[dict]:
    """
    Search the Open Textbook Library (open.umn.edu).
    The search endpoint returns an Atom XML feed.
    All OTL books are openly licensed.
    """
    try:
        params = {"q": keywords}
        response = requests.get(OTL_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"atom": ATOM_NS}

        results = []
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            content_el = entry.find("atom:content", ns)

            if title_el is None:
                continue

            title = title_el.text or ""

            # Find the alternate link
            url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("rel") == "alternate":
                    url = link.get("href", "")
                    break

            if not title or not url:
                continue

            # Strip HTML tags and img elements from the content field
            description = ""
            if content_el is not None and content_el.text:
                soup = BeautifulSoup(content_el.text, "html.parser")
                for img in soup.find_all("img"):
                    img.decompose()
                description = soup.get_text(strip=True)

            results.append({
                "title": title,
                "url": url,
                "description": description,
                "license_raw": "CC BY",
                "source": "Open Textbook Library",
                "resource_type": "Open Textbook",
            })

        return results

    except Exception as e:
        print(f"[Open Textbook Library] Error: {e}")
        return []
