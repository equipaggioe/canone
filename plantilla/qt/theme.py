"""Fusion with the generated palette, and frames that show in it."""

from enum import StrEnum
from functools import partial
from typing import cast, override

from PySide6.QtCore import QRect, QRectF, QSettings, Qt
from PySide6.QtGui import QPainter, QPalette, QPen
from PySide6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QStyle,
    QStyleHintReturn,
    QStyleOption,
    QStyleOptionButton,
    QStyleOptionComplex,
    QWidget,
)

from app.colors import INITIAL, ColorTheme, palette

MODE = "mode"
THEME = "theme"

# The fill and the text of a button with the property "variant".
VARIANTS = {"primary": ("primary", "on_primary"), "danger": ("error", "on_error")}


class Mode(StrEnum):
    """The modes the user chooses from."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class Style(QProxyStyle):
    """Fusion, with frames and grids in the colors of the palette.

    Fusion darkens the window color for them, and on a dark window they
    do not show.
    """

    def __init__(self) -> None:
        """Wrap Fusion."""
        super().__init__("Fusion")
        self.colors: dict[str, str] = {}

    @override
    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Draw the frame of a field or a panel in the outline."""
        if element in (QStyle.PrimitiveElement.PE_FrameLineEdit, QStyle.PrimitiveElement.PE_Frame):
            frame(option, painter)
            return
        super().drawPrimitive(element, option, painter, widget)

    @override
    def drawComplexControl(
        self,
        control: QStyle.ComplexControl,
        option: QStyleOptionComplex,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Draw a spin box or a combo box framed in the outline."""
        super().drawComplexControl(control, option, painter, widget)
        if control in (QStyle.ComplexControl.CC_SpinBox, QStyle.ComplexControl.CC_ComboBox):
            frame(option, painter)

    @override
    def drawControl(
        self,
        element: QStyle.ControlElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        """Draw a button with a variant in its colors."""
        variant = str(widget.property("variant")) if widget else ""
        if isinstance(option, QStyleOptionButton) and variant in VARIANTS:
            fill, text = VARIANTS[variant]
            option = QStyleOptionButton(option)
            colors = cast(QPalette, option.palette)
            colors.setColor(QPalette.ColorRole.Button, self.colors[fill])
            colors.setColor(QPalette.ColorRole.ButtonText, self.colors[text])
        super().drawControl(element, option, painter, widget)

    @override
    def styleHint(
        self,
        hint: QStyle.StyleHint,
        option: QStyleOption | None = None,
        widget: QWidget | None = None,
        returnData: QStyleHintReturn | None = None,
    ) -> int:
        """Draw the grid of a table in the outline variant."""
        if hint == QStyle.StyleHint.SH_Table_GridLineColor and option is not None:
            # An opaque QRgb, as the signed int that styleHint returns.
            mid = cast(QPalette, option.palette).color(QPalette.ColorRole.Mid)
            return mid.rgb() - (1 << 32)
        return super().styleHint(hint, option, widget, returnData)


def frame(option: QStyleOption, painter: QPainter) -> None:
    """Draw a frame in Dark, the outline, or in Highlight with focus."""
    # PySide types the fields of a style option as an ellipsis.
    focus = bool(cast(QStyle.StateFlag, option.state) & QStyle.StateFlag.State_HasFocus)
    width = 2 if focus else 1
    role = QPalette.ColorRole.Highlight if focus else QPalette.ColorRole.Dark
    inset = width / 2
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(cast(QPalette, option.palette).color(role), width))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    rect = QRectF(cast(QRect, option.rect)).adjusted(inset, inset, -inset, -inset)
    painter.drawRoundedRect(rect, 2, 2)
    painter.restore()


def apply(app: QApplication) -> None:
    """Set the style and paint the choice, also on a system change."""
    app.setStyle(Style())
    app.styleHints().colorSchemeChanged.connect(partial(paint, app))
    paint(app, app.styleHints().colorScheme())


def chosen_mode() -> Mode:
    """Read the mode the user chose, which starts as the system one."""
    return Mode(QSettings().value(MODE, Mode.SYSTEM.value, type=str))


def chosen_theme() -> ColorTheme:
    """Read the color theme the user chose; the initial one at first."""
    stored = QSettings().value(THEME, "", type=str)
    return ColorTheme[str(stored)] if stored else INITIAL


def choose_mode(app: QApplication, mode: Mode) -> None:
    """Save the mode the user chose and paint it."""
    QSettings().setValue(MODE, mode.value)
    paint(app, app.styleHints().colorScheme())


def choose_theme(app: QApplication, theme: ColorTheme) -> None:
    """Save the color theme the user chose and paint it."""
    QSettings().setValue(THEME, theme.name)
    paint(app, app.styleHints().colorScheme())


def paint(app: QApplication, system: Qt.ColorScheme) -> None:
    """Set the palette of the choice, and its colors in the style."""
    mode = chosen_mode()
    dark = system == Qt.ColorScheme.Dark if mode is Mode.SYSTEM else mode is Mode.DARK
    theme = chosen_theme()
    colors = theme.dark if dark else theme.light
    style = app.style()
    if not isinstance(style, Style):
        raise TypeError("apply() sets the style before painting")
    style.colors = colors
    app.setPalette(palette(colors))
