import re

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above)",
    r"you (must|should) now",
    r"new instructions?:",
    r"system prompt",
]


def contains_injection_attempt(text: str) -> bool:
    ...
