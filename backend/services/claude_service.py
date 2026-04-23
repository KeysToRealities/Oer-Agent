import json
import os
import time
from pathlib import Path

import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_CATALOG_PATH = Path(__file__).parent.parent / "data" / "ggc_courses.json"
_COURSE_CATALOG: dict[str, dict] = {}
if _CATALOG_PATH.exists():
    with open(_CATALOG_PATH) as f:
        _COURSE_CATALOG = json.load(f)

_DESCRIPTION_CACHE: dict[str, str] = {}
_GGC_DETAIL_URL = "https://catalog.ggc.edu/preview_course_nopop.php"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def _lookup_course(query: str) -> dict | None:
    """Return catalog entry {title, coid} if query matches a GGC course code."""
    return _COURSE_CATALOG.get(query.strip().upper())


def _fetch_course_description(coid: str) -> str:
    """Fetch and parse the course description from the GGC detail page. Cached."""
    if coid in _DESCRIPTION_CACHE:
        return _DESCRIPTION_CACHE[coid]
    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(
            _GGC_DETAIL_URL,
            params={"catoid": "49", "coid": coid},
            headers=_HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        block = soup.select_one("td.block_content")
        if not block:
            return ""
        p = block.find("p")
        if not block:
            return ""
        last_br = None
        for br in p.find_all("br"):
            last_br = br
        if last_br is None:
            return ""
        description = "".join(
            str(s).strip() for s in last_br.next_siblings
            if isinstance(s, str)
        ).strip()
        _DESCRIPTION_CACHE[coid] = description
        return description
    except Exception:
        return ""

# Scoring tool schema — forces structured output from Claude
_SCORE_TOOL = {
    "name": "submit_evaluation",
    "description": "Submit evaluation scores and a relevance explanation for an OER resource.",
    "input_schema": {
        "type": "object",
        "properties": {
            "currency_score": {
                "type": "number",
                "description": (
                    "How current and up-to-date is the resource? "
                    "Consider whether the content reflects recent knowledge, "
                    "active maintenance, and modern presentation. Score 0–5."
                ),
            },
            "pedagogical_value_score": {
                "type": "number",
                "description": (
                    "How strong is the educational and instructional value? "
                    "Consider clarity, depth, structure, learning objectives, "
                    "exercises, and suitability for a college course. Score 0–5."
                ),
            },
            "relevance_score": {
                "type": "number",
                "description": (
                    "How directly relevant is this resource to the student's specific course? "
                    "Score 5 only if the resource is squarely about the course's core subject matter. "
                    "Score 3-4 for resources that cover related subtopics. "
                    "Score 1-2 if the connection is loose or tangential. "
                    "Score 0 if the resource has nothing to do with the course topic. "
                    "Be strict — a resource about immigration, history, or unrelated fields "
                    "should score 0 regardless of its quality. Score 0–5."
                ),
            },
            "technical_quality_score": {
                "type": "number",
                "description": (
                    "How technically sound and well-produced is the resource? "
                    "Consider accuracy, completeness, production quality, "
                    "and accessibility features. Score 0–5."
                ),
            },
            "interactivity_score": {
                "type": "number",
                "description": (
                    "How interactive and engaging is the resource for learners? "
                    "Score 5 for resources with simulations, quizzes, multimedia, or "
                    "hands-on activities. Score 3 for embedded videos or check questions. "
                    "Score 1–2 for primarily static content like plain PDFs or text. Score 0–5."
                ),
            },
            "explanation": {
                "type": "string",
                "description": (
                    "1–2 sentences explaining why this resource is or isn't a good fit "
                    "for the student's course. Be specific and concise."
                ),
            },
        },
        "required": [
            "currency_score",
            "pedagogical_value_score",
            "relevance_score",
            "technical_quality_score",
            "interactivity_score",
            "explanation",
        ],
    },
}


def get_keywords(course: str) -> list[str]:
    """Map a course number/name to 2-3 specific OER search keywords."""
    entry = _lookup_course(course)
    if entry:
        description = _fetch_course_description(entry["coid"])
        if description:
            label = f"'{course}' ({entry['title']}): {description}"
        else:
            label = f"'{course}' ({entry['title']})"
    else:
        label = f"'{course}'"

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": (
                    f"A student is looking for open educational resources for this course: {label}.\n"
                    "Return 2-3 specific academic search keywords that cover the main topics of this course.\n"
                    "Each keyword should be 1-4 words, specific enough to find relevant academic OER materials.\n"
                    "Prefer precise academic terms — e.g. 'digital video production', 'film theory', 'cinematography'.\n"
                    "Do not include words like 'free', 'OER', 'textbook', 'open', or course numbers.\n"
                    "Return one keyword per line, nothing else."
                ),
            }
        ],
    )
    raw = message.content[0].text.strip()
    keywords = [line.strip() for line in raw.splitlines() if line.strip()]
    return keywords[:3]


def score_and_explain_resource(resource: dict, course: str) -> dict:
    """
    Ask Claude to score a resource on four dimensions and generate an explanation.

    Returns a dict with keys:
      currency_score, pedagogical_value_score, relevance_score,
      technical_quality_score, explanation
    On failure returns an empty dict (caller should fall back to heuristics).
    """
    entry = _lookup_course(course)
    if entry:
        desc = _fetch_course_description(entry["coid"])
        course_label = f"{course} ({entry['title']}): {desc}" if desc else f"{course} ({entry['title']})"
    else:
        course_label = course

    prompt = (
        f"A student is searching for OER materials for: {course_label}\n\n"
        f"Resource title: {resource.get('title', 'Unknown')}\n"
        f"Source: {resource.get('source', 'Unknown')}\n"
        f"Type: {resource.get('resource_type') or 'Not specified'}\n"
        f"License: {resource.get('license') or resource.get('license_raw') or 'Unknown'}\n"
        f"Description: {(resource.get('description') or 'No description available.')[:600]}\n\n"
        "Evaluate this resource and submit your scores and explanation."
    )

    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                tools=[_SCORE_TOOL],
                tool_choice={"type": "tool", "name": "submit_evaluation"},
                messages=[{"role": "user", "content": prompt}],
            )
            for block in message.content:
                if block.type == "tool_use":
                    return block.input
            return {}
        except anthropic.RateLimitError:
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
        except Exception as e:
            print(f"[Claude scoring] Error for '{resource.get('title')}': {e}")
            break

    return {}
