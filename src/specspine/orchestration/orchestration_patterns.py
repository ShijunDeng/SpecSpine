from __future__ import annotations

import re

CONTRACT_PATTERN = re.compile(
    r"(?P<type>endpoint|schema|config|api|route|table|collection)\s*[=:]\s*(?P<name>[A-Za-z0-9_/.:-]+)",
    re.IGNORECASE,
)

API_ENDPOINT_PATTERNS = [
    re.compile(r"(?:GET|POST|PUT|DELETE|PATCH)\s+(/[A-Za-z0-9_/.:{}-]+)"),
    re.compile(r"(?:route|endpoint|url|path)\s*[=:]\s*['\"]?(/[A-Za-z0-9_/.:{}-]+)"),
]

SCHEMA_PATTERNS = [
    re.compile(r"(?:schema|model|table|collection)\s*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\(.*Model|:.*BaseModel|:.*Schema)"),
]

CONFIG_PATTERNS = [
    re.compile(r"(?:config|setting|env|variable)\s*[=:]\s*([A-Z_][A-Z0-9_]*)"),
    re.compile(r"(?:key|flag)\s*[=:]\s*['\"]?([a-z_][a-z0-9_.]*)['\"]?"),
]

__all__ = [
    "API_ENDPOINT_PATTERNS",
    "CONFIG_PATTERNS",
    "CONTRACT_PATTERN",
    "SCHEMA_PATTERNS",
]
