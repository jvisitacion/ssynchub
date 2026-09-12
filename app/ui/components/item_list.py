"""Middle panel — list of saved items for the active section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from models.content import ContentItem
from ui.themes.theme_manager import ThemePalette, ThemeManager


class ItemListPanel(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        theme_manager: ThemeManager,
        on_select: Callable[[ContentItem | None], None],
    ) -> None:
        super().__init__(parent, width=240)
        self._theme_manager = theme_manager
        self._on_select = on_select
        self._items: list[ContentItem] = []

        header = ttk.Frame(self)
        header.pack(fill="x", padx=8, pady=(12, 4))
        ttk.Label(header, text="Entries", font=("Segoe UI", 11, "bold")).pack(
            side="left"
        )

        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self._listbox = tk.Listbox(
            list_frame,
            activestyle="none",
            highlightthickness=1,
            selectmode="single",
            font=("Segoe UI", 10),
        )
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scroll.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._listbox.bind("<<ListboxSelect>>", self._handle_select)

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def set_items(self, items: list[ContentItem]) -> None:
        self._items = items
        self._listbox.delete(0, tk.END)
        for item in items:
            label = item.title
            if item.updated_at:
                label += f"  ·  {item.updated_at.strftime('%b %d %H:%M')}"
            self._listbox.insert(tk.END, label)

    def clear_selection(self) -> None:
        self._listbox.selection_clear(0, tk.END)

    def select_item(self, item_id: int | None) -> None:
        if item_id is None:
            self.clear_selection()
            return
        for idx, item in enumerate(self._items):
            if item.id == item_id:
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(idx)
                self._listbox.see(idx)
                break

    def _handle_select(self, _event: tk.Event) -> None:
        selection = self._listbox.curselection()
        if not selection:
            self._on_select(None)
            return
        self._on_select(self._items[selection[0]])

    def apply_theme(self, palette: ThemePalette) -> None:
        self._listbox.configure(
            bg=palette.surface,
            fg=palette.text,
            selectbackground=palette.accent,
            selectforeground="#ffffff",
            highlightbackground=palette.border,
            highlightcolor=palette.accent,
        )
