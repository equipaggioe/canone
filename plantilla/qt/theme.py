"""The design tokens and the one style sheet of the app."""

from PySide6.QtWidgets import QApplication

BACKGROUND = "#ffffff"
SURFACE = "#f3f4f6"
TEXT = "#111827"
PRIMARY = "#2563eb"
ON_PRIMARY = "#ffffff"
DANGER = "#b91c1c"


def apply(app: QApplication) -> None:
    """Set Fusion and the global style sheet."""
    app.setStyle("Fusion")
    app.setStyleSheet(f"""
        QWidget {{ background-color: {BACKGROUND}; color: {TEXT}; }}
        QLineEdit, QTextEdit, QPlainTextEdit, QAbstractItemView {{
            background-color: {SURFACE};
        }}
        QPushButton {{ background-color: {PRIMARY}; color: {ON_PRIMARY}; }}
        QPushButton[variant="danger"] {{ background-color: {DANGER}; }}
    """)
