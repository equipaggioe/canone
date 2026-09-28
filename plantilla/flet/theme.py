"""The design tokens and the light and dark themes."""

import flet as ft

SEED = "#2563eb"


def apply(page: ft.Page) -> None:
    """Set both themes and follow the system mode."""
    page.theme = ft.Theme(color_scheme_seed=SEED)
    page.dark_theme = ft.Theme(color_scheme_seed=SEED)
    page.theme_mode = ft.ThemeMode.SYSTEM
