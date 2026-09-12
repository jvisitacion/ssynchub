"""Startup screen — New Project button and a list of projects to open."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from models.project import Project
from ui.themes.theme_manager import ThemeManager, ThemePalette

CARD_WIDTH = 280
CARD_HEIGHT = 44
CARD_PADY = 6


class ProjectLandingView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        theme_manager: ThemeManager,
        on_new: Callable[[], None],
        on_open: Callable[[Project], None],
        on_rename: Callable[[Project], None],
        on_delete: Callable[[Project], None],
        on_theme_toggle: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self._theme_manager = theme_manager
        self._palette = theme_manager.palette
        self._on_new = on_new
        self._on_open = on_open
        self._on_rename = on_rename
        self._on_delete = on_delete
        self._projects: list[Project] = []
        self._project_rows: list[tk.Frame] = []

        self._header = tk.Frame(self)
        self._header.pack(fill="x", padx=12, pady=(12, 0))
        self._theme_btn = tk.Button(
            self._header,
            text="Theme: Dark",
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=on_theme_toggle,
        )
        self._theme_btn.pack(side="right")

        self._container = tk.Frame(self)
        self._container.place(relx=0.5, rely=0.5, anchor="center")

        self._new_btn = tk.Button(
            self._container,
            text="New Project",
            font=("Segoe UI", 11),
            relief="flat",
            width=24,
            pady=10,
            cursor="hand2",
            command=on_new,
        )
        self._new_btn.pack(pady=(0, CARD_PADY))

        self._list_frame = tk.Frame(self._container)
        self._list_frame.pack()

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self.configure(bg=palette.bg)
        self._header.configure(bg=palette.bg)
        for widget in (self._container, self._list_frame):
            widget.configure(bg=palette.bg)

        self._theme_btn.configure(
            text="Theme: Dark" if palette.name == "dark" else "Theme: Light",
            bg=palette.surface_alt,
            fg=palette.text,
            activebackground=palette.accent_hover,
            activeforeground="#ffffff",
        )

        self._new_btn.configure(
            bg=palette.landing_card,
            fg=palette.landing_card_text,
            activebackground=palette.landing_card_hover,
            activeforeground=palette.landing_card_text,
        )

        if self._projects:
            self.set_projects(self._projects)

    def set_projects(self, projects: list[Project]) -> None:
        self._projects = projects
        for row in self._project_rows:
            row.destroy()
        self._project_rows.clear()

        palette = self._palette
        for project in projects:
            card = tk.Frame(
                self._list_frame,
                bg=palette.landing_card,
                width=CARD_WIDTH,
                height=CARD_HEIGHT,
            )
            card.pack(pady=CARD_PADY)
            card.pack_propagate(False)
            card.grid_columnconfigure(0, weight=1)

            name_btn = tk.Button(
                card,
                text=project.name,
                font=("Segoe UI", 11),
                bg=palette.landing_card,
                fg=palette.landing_card_text,
                activebackground=palette.landing_card_hover,
                activeforeground=palette.landing_card_text,
                relief="flat",
                cursor="hand2",
                command=lambda p=project: self._on_open(p),
            )
            name_btn.grid(row=0, column=0, sticky="ew", padx=(14, 4), pady=8)

            menu_btn = self._create_menu_button(card, project)
            menu_btn.grid(row=0, column=1, padx=(0, 12), pady=10)

            self._project_rows.append(card)

    def _create_menu_button(self, parent: tk.Frame, project: Project) -> tk.Frame:
        palette = self._palette
        btn = tk.Frame(
            parent,
            bg=palette.landing_card,
            cursor="hand2",
            width=16,
            height=24,
        )
        btn.pack_propagate(False)

        def open_menu(_event: tk.Event | None = None) -> None:
            self._show_menu(project, btn)

        def set_bg(color: str) -> None:
            btn.configure(bg=color)
            for child in btn.winfo_children():
                child.configure(bg=color)

        btn.bind("<Button-1>", open_menu)
        btn.bind("<Enter>", lambda _e: set_bg(palette.landing_card_hover))
        btn.bind("<Leave>", lambda _e: set_bg(palette.landing_card))

        for _ in range(3):
            dot = tk.Label(
                btn,
                text="●",
                font=("Segoe UI", 5),
                bg=palette.landing_card,
                fg=palette.landing_card_text,
                cursor="hand2",
            )
            dot.pack(pady=0)
            dot.bind("<Button-1>", open_menu)

        return btn

    def _show_menu(self, project: Project, anchor: tk.Widget) -> None:
        palette = self._palette
        menu = tk.Menu(
            self,
            tearoff=0,
            font=("Segoe UI", 10),
            bg=palette.surface,
            fg=palette.text,
            activebackground=palette.accent,
            activeforeground="#ffffff",
        )
        menu.add_command(label="Rename", command=lambda: self._on_rename(project))
        menu.add_command(label="Delete", command=lambda: self._on_delete(project))
        try:
            x = anchor.winfo_rootx()
            y = anchor.winfo_rooty() + anchor.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
