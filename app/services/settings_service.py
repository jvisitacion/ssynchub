from __future__ import annotations

from db.repository.settings_repository import SettingsRepository


class SettingsService:
    THEME_KEY = "theme"
    VALID_THEMES = ("dark", "light")

    def __init__(self, repository: SettingsRepository | None = None) -> None:
        self._repo = repository or SettingsRepository()

    def get_theme(self) -> str:
        theme = self._repo.get(self.THEME_KEY, "dark")
        return theme if theme in self.VALID_THEMES else "dark"

    def set_theme(self, theme: str) -> str:
        if theme not in self.VALID_THEMES:
            raise ValueError(f"Theme must be one of {self.VALID_THEMES}")
        self._repo.set(self.THEME_KEY, theme)
        return theme

    def toggle_theme(self) -> str:
        current = self.get_theme()
        new_theme = "light" if current == "dark" else "dark"
        return self.set_theme(new_theme)
