import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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
                    "How relevant is this resource to the student's specific course? "
                    "Consider alignment of topics, level, and scope. Score 0–5."
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
            "explanation",
        ],
    },
}


def get_keywords(course: str) -> str:
    """Map a course number/name to useful OER search keywords."""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": (
                    f"A student is looking for open educational resources for this course: '{course}'.\n"
                    "Return the single best search keyword (1–3 words) for finding academic materials on this topic.\n"
                    "Prefer the most common academic term instructors would search — e.g. 'biology', 'calculus', 'English composition'.\n"
                    "Do not use commas or punctuation — just space-separated words.\n"
                    "Do not include words like 'free', 'OER', 'textbook', 'open', or course numbers.\n"
                    "Only return the keyword, nothing else."
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def score_and_explain_resource(resource: dict, course: str) -> dict:
    """
    Ask Claude to score a resource on four dimensions and generate an explanation.

    Returns a dict with keys:
      currency_score, pedagogical_value_score, relevance_score,
      technical_quality_score, explanation
    On failure returns an empty dict (caller should fall back to heuristics).
    """
    prompt = (
        f"A student is searching for OER materials for: '{course}'.\n\n"
        f"Resource title: {resource.get('title', 'Unknown')}\n"
        f"Source: {resource.get('source', 'Unknown')}\n"
        f"Type: {resource.get('resource_type') or 'Not specified'}\n"
        f"License: {resource.get('license') or resource.get('license_raw') or 'Unknown'}\n"
        f"Description: {(resource.get('description') or 'No description available.')[:600]}\n\n"
        "Evaluate this resource and submit your scores and explanation."
    )

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
    except Exception as e:
        print(f"[Claude scoring] Error for '{resource.get('title')}': {e}")

    return {}
