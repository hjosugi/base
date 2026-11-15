"""Count words in text. A small example to try the tools on."""

import re
from collections import Counter

# Letters, digits, "_" and "'". So "don't" is one word.
_WORD = re.compile(r"[\w']+")


def count_words(text: str) -> Counter[str]:
    """Count each word in `text`. Upper and lower case are the same word."""
    return Counter(word.lower() for word in _WORD.findall(text))


def top_words(text: str, limit: int = 10) -> list[tuple[str, int]]:
    """Return the `limit` most common words, most common first.

    Words with the same count are in alphabetical order.
    """
    if limit < 1:
        raise ValueError("limit must be 1 or more")
    counts = count_words(text)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:limit]
