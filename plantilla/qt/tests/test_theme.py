"""The theme rules of qt.md and the design tokens in canone."""

import re
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
PACKAGE = SRC / "app"
THEME = PACKAGE / "theme.py"
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bQColor\(")


def lines_outside_theme(pattern: re.Pattern[str]) -> list[str]:
    """List the lines outside theme.py that match a pattern."""
    return [
        f"{path.relative_to(SRC)}:{number}"
        for path in sorted(PACKAGE.rglob("*.py"))
        if path != THEME
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if pattern.search(line)
    ]


def test_colors_only_in_theme() -> None:
    """No color literal lives outside the tokens."""
    assert not lines_outside_theme(COLOR)


def test_style_sheet_only_in_theme() -> None:
    """The app has one style sheet, built in theme.py."""
    assert not lines_outside_theme(re.compile(r"\.setStyleSheet\("))


def test_style_is_fusion() -> None:
    """theme.py sets the Fusion style."""
    assert 'setStyle("Fusion")' in THEME.read_text(encoding="utf-8")
