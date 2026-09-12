"""Strategy pattern — swap entire color palette between dark and light themes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ThemePalette:
    name: str
    bg: str
    surface: str
    surface_alt: str
    border: str
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    danger: str
    success: str
    canvas_bg: str
    shape_fill: str
    shape_outline: str
    line_color: str
    bullet_color: str
    select_color: str
    landing_card: str
    landing_card_hover: str
    landing_card_text: str


THEMES: dict[str, ThemePalette] = {
    "dark": ThemePalette(
        name="dark",
        bg="#1e1e2e",
        surface="#252536",
        surface_alt="#2f2f45",
        border="#3d3d5c",
        text="#e4e4ef",
        text_muted="#9898b0",
        accent="#7c6af7",
        accent_hover="#9585ff",
        danger="#f07178",
        success="#9ece6a",
        canvas_bg="#181825",
        shape_fill="#313244",
        shape_outline="#7c6af7",
        line_color="#89b4fa",
        bullet_color="#fab387",
        select_color="#f9e2af",
        landing_card="#313244",
        landing_card_hover="#45475a",
        landing_card_text="#e4e4ef",
    ),
    "light": ThemePalette(
        name="light",
        bg="#f5f5f7",
        surface="#ffffff",
        surface_alt="#eef0f4",
        border="#d0d4dc",
        text="#1a1a2e",
        text_muted="#6b7280",
        accent="#5b4cdb",
        accent_hover="#4838c7",
        danger="#dc2626",
        success="#16a34a",
        canvas_bg="#fafafa",
        shape_fill="#e8eaf0",
        shape_outline="#5b4cdb",
        line_color="#2563eb",
        bullet_color="#ea580c",
        select_color="#ca8a04",
        landing_card="#66E0E5",
        landing_card_hover="#4dd4db",
        landing_card_text="#000000",
    ),
}


class ThemeManager:
    """Observer hub — widgets register callbacks and get notified on theme change."""

    def __init__(self, initial_theme: str = "dark") -> None:
        self._theme = initial_theme if initial_theme in THEMES else "dark"
        self._observers: list[Callable[[ThemePalette], None]] = []

    @property
    def palette(self) -> ThemePalette:
        return THEMES[self._theme]

    @property
    def current(self) -> str:
        return self._theme

    def set_theme(self, theme: str) -> None:
        if theme not in THEMES:
            raise ValueError(f"Unknown theme: {theme}")
        self._theme = theme
        self._notify()

    def toggle(self) -> str:
        self.set_theme("light" if self._theme == "dark" else "dark")
        return self._theme

    def subscribe(self, callback: Callable[[ThemePalette], None]) -> None:
        self._observers.append(callback)

    def _notify(self) -> None:
        palette = self.palette
        for callback in self._observers:
            callback(palette)
