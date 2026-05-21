from __future__ import annotations

__all__ = [
    "IRREGULAR_VERBS",
    "_get_action_verb_form",
    "_conjugate_verb",
    "_to_gerund",
    "_to_past",
    "_is_cvc",
    "_is_stressed_syllable",
]

IRREGULAR_VERBS = {
    "add": {"base": "add", "gerund": "adding", "past": "added"},
    "create": {"base": "create", "gerund": "creating", "past": "created"},
    "implement": {"base": "implement", "gerund": "implementing", "past": "implemented"},
    "build": {"base": "build", "gerund": "building", "past": "built"},
    "enable": {"base": "enable", "gerund": "enabling", "past": "enabled"},
    "support": {"base": "support", "gerund": "supporting", "past": "supported"},
    "integrate": {"base": "integrate", "gerund": "integrating", "past": "integrated"},
    "introduce": {"base": "introduce", "gerund": "introducing", "past": "introduced"},
    "develop": {"base": "develop", "gerund": "developing", "past": "developed"},
    "design": {"base": "design", "gerund": "designing", "past": "designed"},
    "extend": {"base": "extend", "gerund": "extending", "past": "extended"},
    "provide": {"base": "provide", "gerund": "providing", "past": "provided"},
    "generate": {"base": "generate", "gerund": "generating", "past": "generated"},
    "configure": {"base": "configure", "gerund": "configuring", "past": "configured"},
    "display": {"base": "display", "gerund": "displaying", "past": "displayed"},
    "show": {"base": "show", "gerund": "showing", "past": "showed"},
    "hide": {"base": "hide", "gerund": "hiding", "past": "hid"},
    "remove": {"base": "remove", "gerund": "removing", "past": "removed"},
    "delete": {"base": "delete", "gerund": "deleting", "past": "deleted"},
    "update": {"base": "update", "gerund": "updating", "past": "updated"},
    "modify": {"base": "modify", "gerund": "modifying", "past": "modified"},
    "change": {"base": "change", "gerund": "changing", "past": "changed"},
    "allow": {"base": "allow", "gerund": "allowing", "past": "allowed"},
    "permit": {"base": "permit", "gerund": "permitting", "past": "permitted"},
    "restrict": {"base": "restrict", "gerund": "restricting", "past": "restricted"},
    "block": {"base": "block", "gerund": "blocking", "past": "blocked"},
    "track": {"base": "track", "gerund": "tracking", "past": "tracked"},
    "monitor": {"base": "monitor", "gerund": "monitoring", "past": "monitored"},
    "validate": {"base": "validate", "gerund": "validating", "past": "validated"},
    "verify": {"base": "verify", "gerund": "verifying", "past": "verified"},
    "test": {"base": "test", "gerund": "testing", "past": "tested"},
    "document": {"base": "document", "gerund": "documenting", "past": "documented"},
    "migrate": {"base": "migrate", "gerund": "migrating", "past": "migrated"},
    "convert": {"base": "convert", "gerund": "converting", "past": "converted"},
    "import": {"base": "import", "gerund": "importing", "past": "imported"},
    "export": {"base": "export", "gerund": "exporting", "past": "exported"},
    "publish": {"base": "publish", "gerund": "publishing", "past": "published"},
    "deploy": {"base": "deploy", "gerund": "deploying", "past": "deployed"},
    "render": {"base": "render", "gerund": "rendering", "past": "rendered"},
    "animate": {"base": "animate", "gerund": "animating", "past": "animated"},
    "sync": {"base": "sync", "gerund": "syncing", "past": "synced"},
}


def _get_action_verb_form(action: str, form: str = "base") -> str:
    """Convert action verb to appropriate grammatical form."""
    if action in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[action].get(form, action)
    return _conjugate_verb(action, form)


def _conjugate_verb(verb: str, form: str) -> str:
    """Apply English conjugation rules for verbs not in the explicit table."""
    if form == "base":
        return verb
    if form == "gerund":
        return _to_gerund(verb)
    if form == "past":
        return _to_past(verb)
    return verb


def _to_gerund(verb: str) -> str:
    """Convert verb to gerund (-ing) form."""
    if not verb:
        return verb
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("ee"):
        return verb + "ing"
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ing"
    return verb + "ing"


def _to_past(verb: str) -> str:
    """Convert verb to past tense (-ed) form."""
    if not verb:
        return verb
    if verb.endswith("e"):
        return verb + "d"
    if verb.endswith("y") and len(verb) >= 2 and verb[-2] not in "aeiou":
        return verb[:-1] + "ied"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ed"
    return verb + "ed"


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
