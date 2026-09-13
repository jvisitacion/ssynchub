# application controller - wires UI events to services (MVC-style)
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from db.connection import DatabaseConnection
from models.content import ContentItem, ContentType
from models.project import Project
from services.content_service import ContentService
from services.draft_store import DraftStore
from services.project_service import ProjectService
from services.settings_service import SettingsService
from ui.components.sidebar import Sidebar
from ui.components.toolbar import EditorToolbar
from ui.themes.theme_manager import ThemeManager, ThemePalette
from ui.views.content_view import ContentView
from ui.views.project_landing_view import ProjectLandingView

LANDING_GEOMETRY = "360x520"
DASHBOARD_GEOMETRY = "1100x780"


class SyncHubApp(tk.Tk):
    APP_TITLE = "System Sync Hub"
    MIN_WIDTH = 900
    MIN_HEIGHT = 700

    def __init__(self) -> None:
        super().__init__()
        self.title(self.APP_TITLE)
        self.geometry(LANDING_GEOMETRY)
        self.minsize(320, 400)

        self._project_service = ProjectService()
        self._content_service = ContentService()
        self._settings_service = SettingsService()
        self._theme_manager = ThemeManager(self._settings_service.get_theme())
        self._draft_store = DraftStore()

        self._current_project: Project | None = None
        self._current_type: ContentType = ContentType.DEVELOPMENT_TASKS
        self._current_section: ContentItem | None = None
        self._dirty = False
        self._on_dashboard = False

        self._setup_styles()
        self._build_layout()
        self._theme_manager.subscribe(self._apply_root_theme)
        self._apply_root_theme(self._theme_manager.palette)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._show_landing()

    def _setup_styles(self) -> None:
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

    def _build_layout(self) -> None:
        self._landing_view = ProjectLandingView(
            self,
            self._theme_manager,
            on_new=self._on_landing_new_project,
            on_open=self._open_project,
            on_rename=self._on_landing_rename_project,
            on_delete=self._on_landing_delete_project,
            on_theme_toggle=self._on_theme_toggle,
        )

        self._dashboard_frame = ttk.Frame(self)

        self._toolbar = EditorToolbar(
            self._dashboard_frame,
            self._theme_manager,
            on_save=self._on_save,
            on_theme_toggle=self._on_theme_toggle,
            on_back=self._show_landing,
        )
        self._toolbar.pack(fill="x")

        body = ttk.Panedwindow(self._dashboard_frame, orient="horizontal")
        body.pack(fill="both", expand=True)

        self._sidebar = Sidebar(
            body, self._theme_manager, on_select=self._on_section_change
        )
        body.add(self._sidebar, weight=0)

        self._content_view = ContentView(body, self._theme_manager)
        self._content_view.set_on_change(self._mark_dirty)
        body.add(self._content_view, weight=1)

        self._sidebar.select(self._current_type)

    def _apply_root_theme(self, palette: ThemePalette) -> None:
        self.configure(bg=palette.bg)
        if not self._on_dashboard:
            return
        self.style.configure(".", background=palette.bg, foreground=palette.text)
        self.style.configure("TFrame", background=palette.bg)
        self.style.configure("TPanedwindow", background=palette.bg)
        self.style.configure("TLabel", background=palette.bg, foreground=palette.text)
        self.style.configure(
            "TButton",
            background=palette.surface_alt,
            foreground=palette.text,
        )
        self.style.map(
            "TButton",
            background=[("active", palette.accent_hover)],
            foreground=[("active", "#ffffff")],
        )
        self.style.configure("TEntry", fieldbackground=palette.surface, foreground=palette.text)
        self.style.configure("Vertical.TScrollbar", background=palette.surface_alt)

    def _show_landing(self) -> None:
        if self._on_dashboard and self._current_project and self._current_project.id is not None:
            self._stash_current_section()
            if self._draft_store.has_dirty_in_project(self._current_project.id):
                if not messagebox.askyesno(
                    "Unsaved Changes",
                    "You have unsaved changes. Return to projects anyway?",
                ):
                    return

        self._on_dashboard = False
        self._dashboard_frame.pack_forget()
        self._landing_view.pack(fill="both", expand=True)
        self.minsize(320, 400)
        self.geometry(LANDING_GEOMETRY)
        self.title(self.APP_TITLE)
        self._apply_root_theme(self._theme_manager.palette)
        self._refresh_projects()

    def _open_project(self, project: Project) -> None:
        self._landing_view.pack_forget()
        self._dashboard_frame.pack(fill="both", expand=True)
        self._on_dashboard = True
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.geometry(DASHBOARD_GEOMETRY)
        self.title(f"{self.APP_TITLE} — {project.name}")
        self._apply_root_theme(self._theme_manager.palette)
        self._activate_project(project, initial=True)

    def _refresh_projects(self) -> None:
        try:
            projects = self._project_service.list_projects()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
            projects = []
        self._landing_view.set_projects(projects)

    def _mark_dirty(self) -> None:
        self._dirty = True

    def _section_draft_key(self) -> tuple[int, ContentType] | None:
        if not self._current_project or self._current_project.id is None:
            return None
        return DraftStore.key(self._current_project.id, self._current_type)

    def _stash_current_section(self) -> None:
        draft_key = self._section_draft_key()
        if draft_key is None or self._current_project is None or self._current_section is None:
            return
        item = self._content_view.build_item(
            self._current_project.id,
            self._current_type,
            self._current_section.id,
        )
        self._draft_store.stash(draft_key, item, is_dirty=self._dirty)

    def _load_current_section(self) -> None:
        if not self._current_project or self._current_project.id is None:
            self._current_section = None
            self._dirty = False
            self._content_view.clear()
            return

        draft_key = DraftStore.key(self._current_project.id, self._current_type)
        draft = self._draft_store.get(draft_key)
        if draft:
            self._current_section = draft
            self._content_view.load_item(draft)
            self._dirty = self._draft_store.is_dirty(draft_key)
        else:
            section = self._content_service.get_section(
                self._current_project.id, self._current_type
            )
            if section is None:
                self._content_service.initialize_sections(self._current_project.id)
                section = self._content_service.get_section(
                    self._current_project.id, self._current_type
                )
            self._current_section = section
            self._content_view.load_item(section)
            self._dirty = False

        req = "required" if self._current_type.required else "optional"
        status = f"{self._current_project.name} · {self._current_type.label} ({req})"
        if self._dirty:
            status += " · unsaved"
        self._toolbar.set_status(status)

    def _activate_project(self, project: Project, *, initial: bool = False) -> None:
        self._current_project = project
        self._content_service.initialize_sections(project.id)
        self._sidebar.set_project_name(project.name)
        self._content_view.set_content_type(self._current_type)
        self._sidebar.select(self._current_type)
        self._load_current_section()
        if not initial:
            self._toolbar.set_status(f"Project: {project.name}")

    def _on_landing_new_project(self) -> None:
        name = simpledialog.askstring("New Project", "Project name:", parent=self)
        if not name or not name.strip():
            return
        try:
            self._project_service.create(name.strip())
            self._refresh_projects()
        except Exception as exc:
            messagebox.showerror("Create Project Failed", str(exc))

    def _on_landing_rename_project(self, project: Project) -> None:
        if project.id is None:
            return
        name = simpledialog.askstring(
            "Rename Project", "New name:", initialvalue=project.name, parent=self
        )
        if not name or not name.strip():
            return
        try:
            updated = self._project_service.rename(project.id, name.strip())
            if self._current_project and self._current_project.id == updated.id:
                self._current_project = updated
            self._refresh_projects()
        except Exception as exc:
            messagebox.showerror("Rename Failed", str(exc))

    def _on_landing_delete_project(self, project: Project) -> None:
        if project.id is None:
            return
        if not messagebox.askyesno(
            "Delete Project",
            f"Delete '{project.name}' and all of its sections?\nThis cannot be undone.",
        ):
            return
        try:
            self._project_service.delete(project.id)
            self._draft_store.clear_project(project.id)
            if self._current_project and self._current_project.id == project.id:
                self._current_project = None
                self._current_section = None
                self._dirty = False
            self._refresh_projects()
        except Exception as exc:
            messagebox.showerror("Delete Failed", str(exc))

    def _on_section_change(self, content_type: ContentType) -> None:
        if content_type == self._current_type:
            return
        if not self._current_project:
            self._sidebar.select(self._current_type)
            return
        self._stash_current_section()
        self._current_type = content_type
        self._sidebar.select(content_type)
        self._content_view.set_content_type(content_type)
        self._load_current_section()

    def _on_save(self) -> None:
        if not self._current_project or self._current_project.id is None:
            return
        if not self._current_section:
            return
        try:
            draft_key = self._section_draft_key()
            item = self._content_view.build_item(
                self._current_project.id,
                self._current_type,
                self._current_section.id,
            )
            saved = self._content_service.save_section(item)
            self._current_section = saved
            self._dirty = False
            if draft_key:
                self._draft_store.stash(draft_key, saved, is_dirty=False)
            req = "required" if self._current_type.required else "optional"
            self._toolbar.set_status(
                f"Saved {self._current_type.label} ({req}) · {saved.title}"
            )
        except Exception as exc:
            messagebox.showerror("Save Failed", str(exc))

    def _on_theme_toggle(self) -> None:
        try:
            new_theme = self._settings_service.toggle_theme()
            self._theme_manager.set_theme(new_theme)
        except Exception as exc:
            messagebox.showerror("Theme Error", str(exc))

    def _on_close(self) -> None:
        if self._on_dashboard and self._current_project and self._current_project.id is not None:
            self._stash_current_section()
            if self._draft_store.has_dirty_in_project(self._current_project.id):
                if not messagebox.askyesno(
                    "Unsaved Changes",
                    "You have unsaved changes. Close anyway?",
                ):
                    return
        self.destroy()


def launch_app() -> None:
    db = DatabaseConnection()
    if not db.ping():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Connection Failed",
            "Could not connect to PostgreSQL.\n\n"
            "Check that PostgreSQL is running and your .env settings are correct.\n"
            "Expected database: sync-hub on localhost:5432",
        )
        root.destroy()
        return

    db.initialize_schema()
    app = SyncHubApp()
    app.mainloop()
