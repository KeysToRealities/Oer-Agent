import re

OPEN_LICENSE_PATTERNS = [
    r"cc[\s\-]by",
    r"cc0",
    r"creative commons",
    r"public domain",
    r"mit",
    r"gpl",
    r"apache",
]


def check_license(license_raw: str) -> str | None:
    """
    Return the normalized license string if it's an open license, else None.
    """
    if not license_raw:
        return None

    text = license_raw.lower()
    for pattern in OPEN_LICENSE_PATTERNS:
        if re.search(pattern, text):
            return license_raw.strip()

    return None
