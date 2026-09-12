"""Left navigation — one button per content section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from models.content import ContentType
from ui.themes.theme_manager import ThemePalette, ThemeManager


class Sidebar(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        theme_manager: ThemeManager,
        on_select: Callable[[ContentType], None],
    ) -> None:
        super().__init__(parent, width=220)
        self._theme_manager = theme_manager
        self._on_select = on_select
        self._buttons: dict[ContentType, tk.Button] = {}
        self._active: ContentType | None = None

        self._title_label = ttk.Label(self, text="", font=("Segoe UI", 14, "bold"))
        self._title_label.pack(anchor="w", padx=12, pady=(16, 8))
        ttk.Separator(self).pack(fill="x", padx=8, pady=4)

        for content_type in ContentType:
            btn = tk.Button(
                self,
                text=content_type.sidebar_label,
                anchor="w",
                relief="flat",
                padx=12,
                pady=8,
                command=lambda ct=content_type: self._select(ct),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self._buttons[content_type] = btn

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def set_project_name(self, name: str) -> None:
        self._title_label.configure(text=name)

    def _select(self, content_type: ContentType) -> None:
        self._active = content_type
        self._refresh_buttons()
        self._on_select(content_type)

    def select(self, content_type: ContentType) -> None:
        self._active = content_type
        self._refresh_buttons()

    def _refresh_buttons(self) -> None:
        palette = self._theme_manager.palette
        for ct, btn in self._buttons.items():
            if ct is self._active:
                btn.configure(
                    bg=palette.accent,
                    fg="#ffffff",
                    activebackground=palette.accent_hover,
                )
            else:
                btn.configure(
                    bg=palette.surface,
                    fg=palette.text,
                    activebackground=palette.surface_alt,
                )

    def apply_theme(self, palette: ThemePalette) -> None:
        self.configure(style="Sidebar.TFrame")
        self._refresh_buttons()
