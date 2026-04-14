import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_keywords(course: str) -> str:
    """Map a course number/name to useful OER search keywords."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
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


def generate_explanation(resource: dict, keywords: str) -> str:
    """Generate a short explanation of why a resource is relevant."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=128,
        messages=[
            {
                "role": "user",
                "content": (
                    f"In 1–2 sentences, explain why this resource is relevant for a student searching: '{keywords}'.\n"
                    f"Resource title: {resource.get('title', 'Unknown')}\n"
                    f"Resource description: {resource.get('description', 'No description available.')}\n"
                    "Only return the explanation, nothing else."
                ),
            }
        ],
    )
    return message.content[0].text.strip()
