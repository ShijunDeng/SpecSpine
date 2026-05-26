from __future__ import annotations

import re

__all__ = [
    "COMPONENT_SPLITTERS",
    "MAX_INTENT_CHARS",
    "MODIFIER_PREPOSITIONS",
    "STOP_WORDS",
]

MODIFIER_PREPOSITIONS = (
    "with",
    "when",
    "if",
    "for",
    "to",
    "where",
    "while",
    "unless",
    "after",
    "before",
    "during",
    "without",
    "by",
    "via",
    "through",
    "on",
    "in",
    "at",
    "from",
    "between",
    "among",
)

COMPONENT_SPLITTERS = re.compile(r"\band\b|\bwith\b|\bplus\b|;")

STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "my", "your", "his", "its", "our", "their",
    "mine", "yours", "hers", "ours", "theirs",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
    "this", "that", "these", "those",
    "what", "which", "who", "whom", "whose",
    "and", "but", "or", "nor", "for", "yet", "so",
    "if", "then", "than", "else",
    "because", "as", "until", "while", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "many", "much", "some", "any",
    "no", "not", "only", "own", "same", "such",
    "just", "also", "too", "very", "really", "quite", "rather",
    "of", "in", "to", "for", "with", "on", "at", "from", "by", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "again", "further", "once", "here", "there",
    "up", "down", "out", "off", "over", "under", "more", "most",
    "other", "another", "even", "still", "already", "always", "never",
    "sometimes", "often", "usually", "generally", "commonly",
})

MAX_INTENT_CHARS = 5000
