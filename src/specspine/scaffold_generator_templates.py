from __future__ import annotations

from .scaffold_generator_utils import _slug_to_camel, _ac_id_snake, _extract_ac_keyword

__all__ = [
    "_generate_test_method",
    "_generate_test_class",
]


def _generate_test_method(ac_id: str, ac_text: str, slug: str) -> dict[str, str]:
    camel = _slug_to_camel(slug)
    snake = _ac_id_snake(ac_id)
    keyword = _extract_ac_keyword(ac_text)
    method_name = f"test_{snake}_{keyword}"
    docstring = ac_text.strip()
    body = 'self.fail("TODO: implement")'
    return {
        "method_name": method_name,
        "docstring": docstring,
        "body": body,
    }


def _generate_test_class(slug: str, methods: list[dict[str, str]]) -> str:
    camel = _slug_to_camel(slug)
    class_name = f"{camel}ScaffoldTests"
    lines = [
        '"""Auto-generated test scaffold for feature: {slug}."""',
        "import unittest",
        "",
        "",
        f"class {class_name}(unittest.TestCase):",
    ]
    if not methods:
        lines.append('    """No acceptance criteria found to scaffold."""')
        lines.append("")
        lines.append("    def test_no_criteria(self) -> None:")
        lines.append('        self.fail("TODO: add acceptance criteria to the feature spec")')
    else:
        for i, method in enumerate(methods):
            if i > 0:
                lines.append("")
            method_name = method["method_name"]
            docstring = method["docstring"]
            body = method["body"]
            lines.append(f'    def {method_name}(self) -> None:')
            lines.append(f'        """{docstring}."""')
            lines.append(f"        {body}")
    lines.append("")
    return "\n".join(lines)
