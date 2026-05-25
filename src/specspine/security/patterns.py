from __future__ import annotations

__all__ = [
    "_CUE_PATTERNS",
]

_CUE_PATTERNS: tuple[tuple[str, str, str, str, str], ...] = (
    ("token", r"\btoken\b", "medium", "credential", "Token-related text changed."),
    ("secret", r"\bsecret\b", "high", "credential", "Secret-related text changed."),
    ("password", r"\bpassword\b", "high", "credential", "Password-related text changed."),
    ("api_key", r"\bapi[_-]?key\b", "high", "credential", "API key-related text changed."),
    ("private_key", r"\bprivate[_ -]?key\b", "high", "credential", "Private key-related text changed."),
    ("auth", r"\bauth(?:entication|orization)?\b", "medium", "auth", "Authentication-related text changed."),
    ("session", r"\bsession\b", "medium", "auth", "Session-related text changed."),
    ("cookie", r"\bcookie\b", "medium", "auth", "Cookie-related text changed."),
    ("cors", r"\bcors\b", "medium", "web", "CORS-related text changed."),
    ("sql", r"\bsql\b", "medium", "data", "SQL-related text changed."),
    ("query", r"\bquery\b", "low", "data", "Query-related text changed."),
    ("subprocess", r"\bsubprocess\b", "high", "execution", "Subprocess-related text changed."),
    ("shell", r"\bshell\b", "high", "execution", "Shell-related text changed."),
    ("eval", r"\beval\b", "high", "execution", "Dynamic evaluation text changed."),
    ("exec", r"\bexec\b", "high", "execution", "Dynamic execution text changed."),
    ("pickle", r"\bpickle\b", "high", "deserialization", "Pickle-related text changed."),
    ("yaml.load", r"\byaml\.load\b", "high", "deserialization", "YAML load-related text changed."),
    ("requests", r"\brequests\b", "medium", "network", "Requests-related text changed."),
    ("urlopen", r"\burlopen\b", "medium", "network", "URL opening-related text changed."),
    ("socket", r"\bsocket\b", "medium", "network", "Socket-related text changed."),
    ("crypto", r"\bcrypto(?:graphy)?\b", "medium", "crypto", "Cryptography-related text changed."),
    ("hash", r"\bhash\b", "low", "crypto", "Hash-related text changed."),
    ("random", r"\brandom\b", "low", "crypto", "Randomness-related text changed."),
    ("permission", r"\bpermission\b", "medium", "authorization", "Permission-related text changed."),
    ("admin", r"\badmin\b", "medium", "authorization", "Admin-related text changed."),
    ("path traversal", r"\bpath traversal\b", "high", "filesystem", "Path traversal-related text changed."),
    ("../", r"\.\./", "high", "filesystem", "Parent-directory traversal text changed."),
)
