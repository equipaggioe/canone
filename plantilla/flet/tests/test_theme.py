"""The design tokens in canone: colors live only in theme.py."""

import re
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
THEME = SRC / "theme.py"
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\bColors\.[A-Z]")


def test_colors_only_in_theme() -> None:
    """No color literal lives outside the tokens."""
    offenders = [
        f"{path.relative_to(SRC)}:{number}"
        for path in sorted(SRC.rglob("*.py"))
        if path != THEME
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if COLOR.search(line)
    ]
    assert not offenders
