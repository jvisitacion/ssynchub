from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from typing import Callable

from models.content import ContentItem, ContentType
from ui.components.diagram_editor import DiagramEditor
from ui.themes.theme_manager import ThemePalette, ThemeManager


class ContentView(ttk.Frame):
    def __init__(self, parent: tk.Misc, theme_manager: ThemeManager) -> None:
        super().__init__(parent)
        self._theme_manager = theme_manager
        self._current_type: ContentType | None = None
        self._on_change: Callable[[], None] | None = None

        title_row = ttk.Frame(self)
        title_row.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(title_row, text="Title").pack(side="left")
        self._title_var = tk.StringVar(value="Untitled")
        self._title_entry = ttk.Entry(title_row, textvariable=self._title_var, font=("Segoe UI", 11))
        self._title_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._title_entry.bind("<KeyRelease>", self._notify_change)

        text_label = ttk.Label(self, text="Notes", font=("Segoe UI", 10, "bold"))
        text_label.pack(anchor="w", padx=12, pady=(8, 2))

        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=12, pady=4)

        self._text = tk.Text(
            text_frame,
            wrap="word",
            font=("Segoe UI", 10),
            padx=8,
            pady=8,
            undo=True,
        )
        text_scroll = ttk.Scrollbar(text_frame, command=self._text.yview)
        self._text.configure(yscrollcommand=text_scroll.set)
        self._text.pack(side="left", fill="both", expand=True)
        text_scroll.pack(side="right", fill="y")
        self._text.bind("<<Modified>>", self._on_text_modified)

        self._attachment_frame = ttk.Frame(self)
        self._attachment_label = ttk.Label(
            self._attachment_frame,
            text="Meeting recordings: upload support coming soon.",
            font=("Segoe UI", 9, "italic"),
        )
        self._attachment_label.pack(anchor="w", padx=12, pady=4)

        self._diagram = DiagramEditor(self, theme_manager)

        theme_manager.subscribe(self.apply_theme)
        self.apply_theme(theme_manager.palette)

    def set_on_change(self, callback: Callable[[], None]) -> None:
        self._on_change = callback

    def _notify_change(self, _event: tk.Event | None = None) -> None:
        if self._on_change:
            self._on_change()

    def _on_text_modified(self, _event: tk.Event) -> None:
        if self._text.edit_modified():
            self._notify_change()
            self._text.edit_modified(False)

    def set_content_type(self, content_type: ContentType) -> None:
        self._current_type = content_type
        self._diagram.pack_forget()
        self._attachment_frame.pack_forget()

        if content_type.supports_attachment:
            self._attachment_frame.pack(fill="x", padx=12, pady=4, after=self._text.master)

        if content_type.supports_diagram:
            self._diagram.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            self._text.master.pack_configure(expand=False)
        else:
            self._text.master.pack_configure(expand=True)

    def load_item(self, item: ContentItem | None) -> None:
        from models.content import DiagramData

        self._text.delete("1.0", tk.END)
        if item is None:
            self._title_var.set("Untitled")
            if self._current_type and self._current_type.supports_diagram:
                self._diagram.load_data(DiagramData())
            return

        self._title_var.set(item.title)
        self._text.insert("1.0", item.text_content)
        if self._current_type and self._current_type.supports_diagram:
            self._diagram.load_data(item.diagram_data)

    def clear(self) -> None:
        self._title_var.set("Untitled")
        self._text.delete("1.0", tk.END)
        if self._current_type and self._current_type.supports_diagram:
            from models.content import DiagramData
            self._diagram.load_data(DiagramData())

    def build_item(
        self,
        project_id: int,
        content_type: ContentType,
        item_id: int | None,
    ) -> ContentItem:
        from models.content import ContentItem, DiagramData

        diagram = self._diagram.get_data() if content_type.supports_diagram else DiagramData()
        return ContentItem(
            id=item_id,
            project_id=project_id,
            content_type=content_type,
            title=self._title_var.get(),
            text_content=self._text.get("1.0", "end-1c"),
            diagram_data=diagram,
            attachment_path=None,
        )

    def apply_theme(self, palette: ThemePalette) -> None:
        self._text.configure(
            bg=palette.surface,
            fg=palette.text,
            insertbackground=palette.text,
            selectbackground=palette.accent,
            highlightbackground=palette.border,
        )
        self._attachment_label.configure(foreground=palette.text_muted)
