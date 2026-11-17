"""Fusion, the generated palette and the one style sheet of the app."""

from enum import StrEnum
from functools import partial

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication

from app import colors

KEY = "theme"


class Mode(StrEnum):
    """The modes the user chooses from."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


def apply(app: QApplication) -> None:
    """Set Fusion and paint the mode the user chose."""
    app.setStyle("Fusion")
    app.styleHints().colorSchemeChanged.connect(partial(follow, app))
    paint(app, chosen())


def chosen() -> Mode:
    """Read the mode the user chose, which starts as the system one."""
    return Mode(QSettings().value(KEY, Mode.SYSTEM.value, type=str))


def choose(app: QApplication, mode: Mode) -> None:
    """Save the mode the user chose and paint it."""
    QSettings().setValue(KEY, mode.value)
    paint(app, mode)


def follow(app: QApplication, scheme: Qt.ColorScheme) -> None:
    """Repaint with the system scheme while the user follows it."""
    if chosen() is Mode.SYSTEM:
        paint(app, Mode.DARK if scheme == Qt.ColorScheme.Dark else Mode.LIGHT)


def paint(app: QApplication, mode: Mode) -> None:
    """Set the palette and the style sheet of one mode."""
    if mode is Mode.SYSTEM:
        dark = app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    else:
        dark = mode is Mode.DARK
    current = colors.DARK if dark else colors.LIGHT
    app.setPalette(colors.palette(current))
    app.setStyleSheet(f"""
        QPushButton[variant="primary"] {{
            background-color: {current["primary"]};
            color: {current["on_primary"]};
        }}
        QPushButton[variant="danger"] {{
            background-color: {current["error"]};
            color: {current["on_error"]};
        }}
    """)
