"""Canvas-based diagram editor — shapes, lines, arrows, and bullet notes."""

from __future__ import annotations

import tkinter as tk
from tkinter import simpledialog, ttk
from typing import Any

from models.content import DiagramData
from ui.themes.theme_manager import ThemePalette, ThemeManager

ToolName = str  # "select" | "rect" | "oval" | "line" | "bullet"


class DiagramEditor(ttk.Frame):
    """Interactive canvas; serializes to DiagramData for PostgreSQL JSONB storage."""

    def __init__(self, parent: tk.Misc, theme_manager: ThemeManager) -> None:
        super().__init__(parent)
        self._theme_manager = theme_manager
        self._palette = theme_manager.palette
        self._tool: ToolName = "select"
        self._start_x = 0
        self._start_y = 0
        self._temp_id: int | None = None
        self._selected_tag: str | None = None
        self._next_id = 1

        self._build_toolbar()
        self._canvas = tk.Canvas(
            self,
            bg=self._palette.canvas_bg,
            highlightthickness=1,
            highlightbackground=self._palette.border,
        )
        self._canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._bind_canvas_events()
        theme_manager.subscribe(self.apply_theme)

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)
        ttk.Label(bar, text="Diagram", font=("Segoe UI", 10, "bold")).pack(
            side="left", padx=(0, 12)
        )
        tools = [
            ("Select", "select"),
            ("Rectangle", "rect"),
            ("Oval", "oval"),
            ("Line", "line"),
            ("Arrow", "arrow"),
            ("Bullet", "bullet"),
        ]
        self._tool_buttons: dict[str, ttk.Button] = {}
        for label, tool in tools:
            btn = ttk.Button(
                bar,
                text=label,
                width=9,
                command=lambda t=tool: self._set_tool(t),
            )
            btn.pack(side="left", padx=2)
            self._tool_buttons[tool] = btn

        ttk.Button(bar, text="Delete", width=8, command=self._delete_selected).pack(
            side="right", padx=4
        )
        ttk.Button(bar, text="Clear", width=8, command=self.clear).pack(
            side="right", padx=4
        )

    def _set_tool(self, tool: ToolName) -> None:
        self._tool = tool
        self._deselect()

    def _bind_canvas_events(self) -> None:
        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Double-Button-1>", self._on_double_click)

    def _tag(self) -> str:
        tag = f"item_{self._next_id}"
        self._next_id += 1
        return tag

    def _on_press(self, event: tk.Event) -> None:
        x, y = event.x, event.y
        self._start_x, self._start_y = x, y

        if self._tool == "select":
            clicked = self._canvas.find_withtag("current")
            if clicked:
                tags = self._canvas.gettags(clicked[0])
                item_tags = [t for t in tags if t.startswith("item_")]
                if item_tags:
                    self._select(item_tags[0])
                    return
            self._deselect()
            return

        if self._tool == "bullet":
            text = simpledialog.askstring("Bullet", "Enter bullet text:", parent=self.winfo_toplevel())
            if text:
                self._add_bullet(x, y, text)
            return

        if self._tool in ("rect", "oval"):
            self._temp_id = self._canvas.create_rectangle(
                x, y, x, y,
                outline=self._palette.shape_outline,
                width=2,
                tags=("temp",),
            )
        elif self._tool in ("line", "arrow"):
            self._temp_id = self._canvas.create_line(
                x, y, x, y,
                fill=self._palette.line_color,
                width=2,
                arrow=tk.LAST if self._tool == "arrow" else None,
                tags=("temp",),
            )

    def _on_drag(self, event: tk.Event) -> None:
        if self._temp_id is None:
            return
        x, y = event.x, event.y
        if self._tool in ("rect", "oval"):
            self._canvas.coords(self._temp_id, self._start_x, self._start_y, x, y)
        elif self._tool in ("line", "arrow"):
            self._canvas.coords(self._temp_id, self._start_x, self._start_y, x, y)

    def _on_release(self, event: tk.Event) -> None:
        if self._temp_id is None:
            return
        x, y = event.x, event.y
        if abs(x - self._start_x) < 4 and abs(y - self._start_y) < 4:
            self._canvas.delete(self._temp_id)
            self._temp_id = None
            return

        tag = self._tag()
        coords = (self._start_x, self._start_y, x, y)

        if self._tool == "rect":
            self._canvas.delete(self._temp_id)
            rid = self._canvas.create_rectangle(
                *coords,
                fill=self._palette.shape_fill,
                outline=self._palette.shape_outline,
                width=2,
                tags=(tag, "shape", "rect"),
            )
            self._canvas.addtag_withtag(tag, rid)
        elif self._tool == "oval":
            self._canvas.delete(self._temp_id)
            oid = self._canvas.create_oval(
                *coords,
                fill=self._palette.shape_fill,
                outline=self._palette.shape_outline,
                width=2,
                tags=(tag, "shape", "oval"),
            )
            self._canvas.addtag_withtag(tag, oid)
        elif self._tool in ("line", "arrow"):
            self._canvas.delete(self._temp_id)
            lid = self._canvas.create_line(
                self._start_x, self._start_y, x, y,
                fill=self._palette.line_color,
                width=2,
                arrow=tk.LAST if self._tool == "arrow" else None,
                tags=(tag, "line"),
            )
            self._canvas.addtag_withtag(tag, lid)

        self._temp_id = None

    def _on_double_click(self, event: tk.Event) -> None:
        clicked = self._canvas.find_withtag("current")
        if not clicked:
            return
        tags = self._canvas.gettags(clicked[0])
        item_tags = [t for t in tags if t.startswith("item_")]
        if not item_tags:
            return
        tag = item_tags[0]
        text_ids = self._canvas.find_withtag(tag)
        existing = ""
        for tid in text_ids:
            if "label" in self._canvas.gettags(tid):
                existing = self._canvas.itemcget(tid, "text")
                break
        new_text = simpledialog.askstring(
            "Label", "Shape label:", initialvalue=existing, parent=self.winfo_toplevel()
        )
        if new_text is None:
            return
        for tid in text_ids:
            if "label" in self._canvas.gettags(tid):
                self._canvas.delete(tid)
        if new_text.strip():
            bbox = self._canvas.bbox(tag)
            if bbox:
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                self._canvas.create_text(
                    cx, cy, text=new_text, fill=self._palette.text,
                    font=("Segoe UI", 9), tags=(tag, "label"),
                )

    def _add_bullet(self, x: int, y: int, text: str) -> None:
        tag = self._tag()
        self._canvas.create_text(
            x, y,
            text=f"• {text}",
            anchor="nw",
            fill=self._palette.bullet_color,
            font=("Segoe UI", 10),
            tags=(tag, "bullet"),
        )

    def _select(self, tag: str) -> None:
        self._deselect()
        self._selected_tag = tag
        for item_id in self._canvas.find_withtag(tag):
            item_type = self._canvas.type(item_id)
            if item_type in ("rectangle", "oval", "line"):
                self._canvas.itemconfigure(item_id, outline=self._palette.select_color, width=3)

    def _deselect(self) -> None:
        if not self._selected_tag:
            return
        for item_id in self._canvas.find_withtag(self._selected_tag):
            item_type = self._canvas.type(item_id)
            if item_type in ("rectangle", "oval"):
                self._canvas.itemconfigure(
                    item_id, outline=self._palette.shape_outline, width=2
                )
            elif item_type == "line":
                self._canvas.itemconfigure(item_id, fill=self._palette.line_color, width=2)
        self._selected_tag = None

    def _delete_selected(self) -> None:
        if self._selected_tag:
            self._canvas.delete(self._selected_tag)
            self._selected_tag = None

    def clear(self) -> None:
        self._canvas.delete("all")
        self._selected_tag = None

    def get_data(self) -> DiagramData:
        shapes: list[dict[str, Any]] = []
        lines: list[dict[str, Any]] = []
        bullets: list[dict[str, Any]] = []

        seen_tags: set[str] = set()
        for item_id in self._canvas.find_all():
            tags = self._canvas.gettags(item_id)
            item_tags = [t for t in tags if t.startswith("item_")]
            if not item_tags:
                continue
            tag = item_tags[0]
            if tag in seen_tags:
                continue
            seen_tags.add(tag)

            item_type = self._canvas.type(item_id)
            label = ""
            for tid in self._canvas.find_withtag(tag):
                if "label" in self._canvas.gettags(tid):
                    label = self._canvas.itemcget(tid, "text")

            if "rect" in tags or "oval" in tags:
                coords = self._canvas.coords(item_id)
                shapes.append({
                    "type": "rect" if "rect" in tags else "oval",
                    "coords": coords,
                    "label": label,
                    "tag": tag,
                })
            elif "line" in tags:
                coords = self._canvas.coords(item_id)
                arrow = self._canvas.itemcget(item_id, "arrow") not in ("", "none")
                lines.append({"coords": coords, "arrow": arrow, "tag": tag})
            elif "bullet" in tags:
                coords = self._canvas.coords(item_id)
                text = self._canvas.itemcget(item_id, "text")
                bullets.append({"coords": coords, "text": text, "tag": tag})

        return DiagramData(shapes=shapes, lines=lines, bullets=bullets)

    def load_data(self, data: DiagramData) -> None:
        self.clear()
        max_id = 0
        for shape in data.shapes:
            tag = shape.get("tag") or self._tag()
            max_id = max(max_id, int(tag.split("_")[1]))
            coords = shape["coords"]
            if shape["type"] == "rect":
                self._canvas.create_rectangle(
                    *coords,
                    fill=self._palette.shape_fill,
                    outline=self._palette.shape_outline,
                    width=2,
                    tags=(tag, "shape", "rect"),
                )
            else:
                self._canvas.create_oval(
                    *coords,
                    fill=self._palette.shape_fill,
                    outline=self._palette.shape_outline,
                    width=2,
                    tags=(tag, "shape", "oval"),
                )
            if shape.get("label"):
                cx = (coords[0] + coords[2]) / 2
                cy = (coords[1] + coords[3]) / 2
                self._canvas.create_text(
                    cx, cy, text=shape["label"], fill=self._palette.text,
                    font=("Segoe UI", 9), tags=(tag, "label"),
                )

        for line in data.lines:
            tag = line.get("tag") or self._tag()
            max_id = max(max_id, int(tag.split("_")[1]))
            coords = line["coords"]
            self._canvas.create_line(
                *coords,
                fill=self._palette.line_color,
                width=2,
                arrow=tk.LAST if line.get("arrow") else None,
                tags=(tag, "line"),
            )

        for bullet in data.bullets:
            tag = bullet.get("tag") or self._tag()
            max_id = max(max_id, int(tag.split("_")[1]))
            coords = bullet["coords"]
            self._canvas.create_text(
                coords[0], coords[1],
                text=bullet["text"],
                anchor="nw",
                fill=self._palette.bullet_color,
                font=("Segoe UI", 10),
                tags=(tag, "bullet"),
            )

        self._next_id = max_id + 1

    def apply_theme(self, palette: ThemePalette) -> None:
        self._palette = palette
        self._canvas.configure(
            bg=palette.canvas_bg,
            highlightbackground=palette.border,
        )
        data = self.get_data()
        self.load_data(data)
