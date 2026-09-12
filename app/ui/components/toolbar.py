"""Top toolbar — Save / Theme toggle / back to projects."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ui.themes.theme_manager import ThemePalette, ThemeManager


class EditorToolbar(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        theme_manager: ThemeManager,
        on_save: Callable[[], None],
        on_theme_toggle: Callable[[], None],
        on_back: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme_manager = theme_manager

        if on_back is not None:
            ttk.Button(self, text="← Projects", command=on_back, width=11).pack(
                side="left", padx=(8, 4), pady=6
            )

        self._save_btn = ttk.Button(self, text="Save", command=on_save, width=8)
        self._save_btn.pack(side="left", padx=(8, 4), pady=6)

        self._status = ttk.Label(self, text="Ready")
        self._status.pack(side="left", padx=16)

        self._theme_btn = ttk.Button(
            self, text="Theme: Dark", command=on_theme_toggle, width=14
        )
        self._theme_btn.pack(side="right", padx=8, pady=6)

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def set_status(self, message: str) -> None:
        self._status.configure(text=message)

    def apply_theme(self, palette: ThemePalette) -> None:
        label = "Theme: Dark" if palette.name == "dark" else "Theme: Light"
        self._theme_btn.configure(text=label)
