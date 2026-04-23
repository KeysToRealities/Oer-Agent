"""
One-time script to scrape the GGC course catalog and save to backend/data/ggc_courses.json.
Run from the backend directory:  python tools/scrape_ggc_catalog.py
"""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://catalog.ggc.edu/content.php"
TOTAL_PAGES = 11
OUTPUT = Path(__file__).parent.parent / "data" / "ggc_courses.json"

PARAMS = {
    "catoid": "49",
    "navoid": "7100",
    "filter[item_type]": "3",
    "filter[only_active]": "1",
    "filter[3]": "1",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SEP = "\xa0-\xa0"  # non-breaking space separator used by Acalog


def scrape_page(page: int) -> list[dict]:
    params = {**PARAMS, "filter[cpage]": str(page)}
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    courses = []
    seen = set()
    for a in soup.find_all("a", href=re.compile(r"preview_course_nopop\.php")):
        text = a.get_text(strip=True)
        if SEP not in text:
            continue
        code, _, title = text.partition(SEP)
        code = code.strip()
        title = title.strip()
        href = a.get("href", "")
        coid_match = re.search(r"coid=(\d+)", href)
        coid = coid_match.group(1) if coid_match else None
        if code and title and coid and code not in seen:
            seen.add(code)
            courses.append({"code": code, "title": title, "coid": coid})

    return courses


def main():
    all_courses = {}
    for page in range(1, TOTAL_PAGES + 1):
        print(f"Scraping page {page}/{TOTAL_PAGES}...")
        courses = scrape_page(page)
        for c in courses:
            all_courses[c["code"].upper()] = {"title": c["title"], "coid": c["coid"]}
        time.sleep(0.5)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(all_courses, f, indent=2, sort_keys=True)

    print(f"\nDone. {len(all_courses)} courses saved to {OUTPUT}")


if __name__ == "__main__":
    main()
