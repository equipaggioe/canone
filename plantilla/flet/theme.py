"""The color theme and the mode the user chose."""

import flet as ft

from colors import INITIAL, ColorTheme

MODE = "mode"
THEME = "theme"


async def apply(page: ft.Page, prefs: ft.SharedPreferences) -> None:
    """Paint the color theme and the mode the user chose."""
    paint(page, await chosen_theme(prefs))
    page.theme_mode = await chosen_mode(prefs)


async def chosen_mode(prefs: ft.SharedPreferences) -> ft.ThemeMode:
    """Read the mode the user chose, which starts as the system one."""
    stored = await prefs.get(MODE)
    return ft.ThemeMode.SYSTEM if stored is None else ft.ThemeMode(stored)


async def chosen_theme(prefs: ft.SharedPreferences) -> ColorTheme:
    """Read the color theme the user chose; the initial one at first."""
    stored = await prefs.get(THEME)
    return INITIAL if stored is None else ColorTheme[str(stored)]


async def choose_mode(page: ft.Page, prefs: ft.SharedPreferences, mode: ft.ThemeMode) -> None:
    """Save the mode the user chose and apply it."""
    await prefs.set(MODE, mode.value)
    page.theme_mode = mode
    page.update()


async def choose_theme(page: ft.Page, prefs: ft.SharedPreferences, theme: ColorTheme) -> None:
    """Save the color theme the user chose and paint it."""
    await prefs.set(THEME, theme.name)
    paint(page, theme)
    page.update()


def paint(page: ft.Page, theme: ColorTheme) -> None:
    """Set the light and the dark scheme of one color theme."""
    page.theme = ft.Theme(color_scheme=theme.light)
    page.dark_theme = ft.Theme(color_scheme=theme.dark)
