from PySide6.QtWidgets import QApplication, QWidget


class Colors:
    BG = "#0d1117"
    SURFACE = "#1c212b"
    TEXT = "#e6edf3"
    ACCENT = "#58a6ff"
    DANGER = "#f85149"


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet())


def stylesheet() -> str:
    return f"""
        QWidget {{
            background-color: {Colors.BG};
            color: {Colors.TEXT};
            selection-background-color: {Colors.ACCENT};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit, QAbstractItemView {{
            background-color: {Colors.SURFACE};
        }}
        QPushButton[variant="danger"] {{ background-color: {Colors.DANGER}; }}
    """


def set_variant(widget: QWidget, variant: str) -> None:
    widget.setProperty("variant", variant)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
