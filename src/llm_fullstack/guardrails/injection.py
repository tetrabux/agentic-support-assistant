import re

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above|your) instructions",
    r"disregard (all )?(previous|prior|above)",
    r"you (must|should) now",
    r"new instructions?:",
    r"system prompt",
]


def contains_injection_attempt(text: str) -> bool:
    # Detection only, used to flag traces. Nothing is blocked on this; the actual
    # defence is structural (tool scoping, tenant checks, the approval gate).
    return any(re.search(p, text, re.IGNORECASE) for p in INJECTION_PATTERNS)
