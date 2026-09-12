"""Left panel — project list with create, rename, and delete."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from models.project import Project
from ui.themes.theme_manager import ThemePalette, ThemeManager


class ProjectPanel(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        theme_manager: ThemeManager,
        on_select: Callable[[Project | None], None],
        on_new: Callable[[], None],
        on_rename: Callable[[], None],
        on_delete: Callable[[], None],
    ) -> None:
        super().__init__(parent, width=200)
        self._theme_manager = theme_manager
        self._on_select = on_select
        self._projects: list[Project] = []

        ttk.Label(self, text="Projects", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=(12, 4)
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

        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=8, pady=(4, 12))
        ttk.Button(btn_row, text="New", width=7, command=on_new).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Rename", width=8, command=on_rename).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Delete", width=7, command=on_delete).pack(side="left", padx=2)

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def set_projects(self, projects: list[Project]) -> None:
        self._projects = projects
        self._listbox.delete(0, tk.END)
        for project in projects:
            self._listbox.insert(tk.END, project.name)

    def select_project(self, project_id: int | None) -> None:
        self._listbox.selection_clear(0, tk.END)
        if project_id is None:
            return
        for idx, project in enumerate(self._projects):
            if project.id == project_id:
                self._listbox.selection_set(idx)
                self._listbox.see(idx)
                break

    def get_selected(self) -> Project | None:
        selection = self._listbox.curselection()
        if not selection:
            return None
        return self._projects[selection[0]]

    def _handle_select(self, _event: tk.Event) -> None:
        self._on_select(self.get_selected())

    def apply_theme(self, palette: ThemePalette) -> None:
        self._listbox.configure(
            bg=palette.surface,
            fg=palette.text,
            selectbackground=palette.accent,
            selectforeground="#ffffff",
            highlightbackground=palette.border,
            highlightcolor=palette.accent,
        )
