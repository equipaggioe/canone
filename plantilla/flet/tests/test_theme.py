"""The design tokens in canone: colors live only in colors.py."""

import re
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
COLORS = SRC / "colors.py"
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\bColors\.[A-Z]")


def test_colors_only_generated() -> None:
    """No color literal lives outside the generated schemes."""
    offenders = [
        f"{path.relative_to(SRC)}:{number}"
        for path in sorted(SRC.rglob("*.py"))
        if path != COLORS
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if COLOR.search(line)
    ]
    assert not offenders
