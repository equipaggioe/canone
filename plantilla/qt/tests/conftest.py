"""The `screen` that `test_accessibility.py` measures.

A starting point: each app opens its window with the content one uses,
names its bands, and says what stops its motion and what changes a
state.
"""

from collections.abc import Callable, Iterator, Sequence
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QLocale, QSettings, QTranslator
from PySide6.QtWidgets import QApplication, QWidget
from pytestqt.qtbot import QtBot

from app import theme
from app.services import language
from app.windows.main_window import MainWindow


class AppScreen:
    """The main window, as `test_accessibility.Screen` asks for it."""

    def __init__(self, window: MainWindow) -> None:
        """Keep the window, its bands and its changes of state."""
        self.window: QWidget = window
        # Top to bottom, and left to right: the order Tab goes in.
        self.bands: Sequence[QWidget] = [window.centralWidget()]
        # What changes a state while the focus is elsewhere, by name.
        self.status_changes: Sequence[tuple[str, Callable[[], None]]] = []

    def stop_motion(self) -> None:
        """Stop what moves and what refreshes by itself."""


@pytest.fixture
def screen(qtbot: QtBot, tmp_path: Path) -> Iterator[AppScreen]:
    """Open the window as `main.py` does, with nothing of the user."""
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path))
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    locale = QLocale()
    language.install(app)
    theme.apply(app)
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1400, 860)
    window.show()
    yield AppScreen(window)
    # The translators would pile up in the one QApplication of the run.
    for translator in app.findChildren(QTranslator):
        QCoreApplication.removeTranslator(translator)
        translator.deleteLater()
    QLocale.setDefault(locale)
