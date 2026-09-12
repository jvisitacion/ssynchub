"""Domain models — plain data objects with no UI or DB logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContentType(str, Enum):
    DEVELOPMENT_TASKS = "development_tasks"
    SYSTEM_FLOWS = "system_flows"
    BACKEND_BEHAVIOR = "backend_behavior"
    FRONTEND_BEHAVIOR = "frontend_behavior"
    DATABASE_LOGIC = "database_logic"
    DEBUGGING_IDEAS = "debugging_ideas"
    CONVERSATION_MEETING = "conversation_meeting"

    @property
    def label(self) -> str:
        labels = {
            ContentType.DEVELOPMENT_TASKS: "Development Tasks",
            ContentType.SYSTEM_FLOWS: "System Flows",
            ContentType.BACKEND_BEHAVIOR: "Backend Behavior",
            ContentType.FRONTEND_BEHAVIOR: "Frontend Behavior",
            ContentType.DATABASE_LOGIC: "Database Logic",
            ContentType.DEBUGGING_IDEAS: "Ideas from Debugging Session",
            ContentType.CONVERSATION_MEETING: "Conversation / Meeting",
        }
        return labels[self]

    @property
    def required(self) -> bool:
        return self in (ContentType.DEVELOPMENT_TASKS, ContentType.SYSTEM_FLOWS)

    @property
    def sidebar_label(self) -> str:
        if self.required:
            return self.label
        return f"{self.label} (optional)"

    @property
    def supports_diagram(self) -> bool:
        return self is not ContentType.DEVELOPMENT_TASKS

    @property
    def supports_attachment(self) -> bool:
        return self is ContentType.CONVERSATION_MEETING


@dataclass
class DiagramData:
    """Serializable canvas state stored as JSON in PostgreSQL."""

    shapes: list[dict[str, Any]] = field(default_factory=list)
    lines: list[dict[str, Any]] = field(default_factory=list)
    bullets: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "shapes": self.shapes,
            "lines": self.lines,
            "bullets": self.bullets,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> DiagramData:
        if not data:
            return cls()
        return cls(
            shapes=list(data.get("shapes", [])),
            lines=list(data.get("lines", [])),
            bullets=list(data.get("bullets", [])),
        )


@dataclass
class ContentItem:
    id: int | None
    project_id: int
    content_type: ContentType
    title: str
    text_content: str
    diagram_data: DiagramData = field(default_factory=DiagramData)
    attachment_path: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
