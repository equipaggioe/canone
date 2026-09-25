import re
from pathlib import Path

APP = Path(__file__).parents[1]
THEME = APP / "ui" / "theme.py"
STYLE = re.compile(r"#[0-9a-fA-F]{6}\b|rgba?\(|setStyleSheet\(")


def test_style_only_in_theme() -> None:
    sources = [APP / "main.py", *(APP / "core").rglob("*.py"), *(APP / "ui").rglob("*.py")]
    offenders = [
        f"{path.relative_to(APP)}:{number}"
        for path in sources
        if path != THEME
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if STYLE.search(line)
    ]
    assert not offenders
