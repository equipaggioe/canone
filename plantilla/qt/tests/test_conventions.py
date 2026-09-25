import re
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from ui.theme import apply_theme

APP = Path(__file__).parents[1]
SOURCES = [APP / "main.py", *(APP / "core").rglob("*.py"), *(APP / "ui").rglob("*.py")]


def find(pattern: str) -> list[str]:
    regex = re.compile(pattern)
    return [
        f"{path.relative_to(APP)}:{number}"
        for path in SOURCES
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if regex.search(line)
    ]


def test_exec_has_no_underscore() -> None:
    assert not find(r"\.exec_\(")


def test_single_network_manager() -> None:
    assert len(find(r"\bQNetworkAccessManager\(")) <= 1


def test_network_manager_auto_deletes_replies() -> None:
    managers = find(r"\bQNetworkAccessManager\(")
    assert len(find(r"\.setAutoDeleteReplies\(True\)")) == len(managers)


def test_no_palette() -> None:
    assert not find(r"\.setPalette\(")


def test_style_is_fusion(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    styles: list[str] = []
    monkeypatch.setattr(QApplication, "setStyle", staticmethod(styles.append))
    apply_theme(qapp)
    assert styles == ["Fusion"]
