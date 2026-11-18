"""The light and dark themes, from the generated color schemes."""

import flet as ft

import colors

KEY = "theme"


async def apply(page: ft.Page, prefs: ft.SharedPreferences) -> None:
    """Set both themes and the mode the user chose."""
    page.theme = ft.Theme(color_scheme=colors.LIGHT)
    page.dark_theme = ft.Theme(color_scheme=colors.DARK)
    page.theme_mode = await chosen(prefs)


async def chosen(prefs: ft.SharedPreferences) -> ft.ThemeMode:
    """Read the mode the user chose, which starts as the system one."""
    stored = await prefs.get(KEY)
    return ft.ThemeMode.SYSTEM if stored is None else ft.ThemeMode(stored)


async def choose(page: ft.Page, prefs: ft.SharedPreferences, mode: ft.ThemeMode) -> None:
    """Save the mode the user chose and apply it."""
    await prefs.set(KEY, mode.value)
    page.theme_mode = mode
    page.update()
