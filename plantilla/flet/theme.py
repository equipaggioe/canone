"""The light and dark themes, from the generated color schemes."""

import flet as ft

import colors


def apply(page: ft.Page) -> None:
    """Set both themes and follow the system mode."""
    page.theme = ft.Theme(color_scheme=colors.LIGHT)
    page.dark_theme = ft.Theme(color_scheme=colors.DARK)
    page.theme_mode = ft.ThemeMode.SYSTEM
