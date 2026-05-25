from __future__ import annotations

__all__ = [
    "_is_cvc",
    "_is_stressed_syllable",
]


def _is_cvc(word: str) -> bool:
    """Check if word ends in consonant-vowel-consonant pattern."""
    if len(word) < 3:
        return False
    vowels = set("aeiou")
    return (word[-3] not in vowels and
            word[-2] in vowels and
            word[-1] not in vowels)


def _is_stressed_syllable(word: str) -> bool:
    """Heuristic: single syllable or stress on last syllable."""
    if len(word) <= 2:
        return True
    vowels = set("aeiou")
    vowel_count = sum(1 for c in word.lower() if c in vowels)
    return vowel_count <= 2
