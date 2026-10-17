"""Fusion, the generated palette and the one style sheet of the app."""

from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app import colors


def apply(app: QApplication) -> None:
    """Set Fusion and follow the color scheme of the system."""
    app.setStyle("Fusion")
    hints = app.styleHints()
    hints.colorSchemeChanged.connect(partial(paint, app))
    paint(app, hints.colorScheme())


def paint(app: QApplication, scheme: Qt.ColorScheme) -> None:
    """Set the palette and the style sheet of one mode."""
    current = colors.DARK if scheme == Qt.ColorScheme.Dark else colors.LIGHT
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
