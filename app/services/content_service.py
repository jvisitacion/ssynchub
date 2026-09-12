"""Service layer — business rules between UI (Controller) and Repository."""

from __future__ import annotations

from db.repository.content_repository import ContentRepository
from models.content import ContentItem, ContentType, DiagramData


class ContentService:
    def __init__(self, repository: ContentRepository | None = None) -> None:
        self._repo = repository or ContentRepository()

    def get_section(self, project_id: int, content_type: ContentType) -> ContentItem | None:
        return self._repo.get_by_project_and_type(project_id, content_type)

    def list_sections(self, project_id: int) -> list[ContentItem]:
        return self._repo.get_all_by_project(project_id)

    def initialize_sections(self, project_id: int) -> list[ContentItem]:
        created: list[ContentItem] = []
        for content_type in ContentType:
            existing = self._repo.get_by_project_and_type(project_id, content_type)
            if existing:
                continue
            item = ContentItem(
                id=None,
                project_id=project_id,
                content_type=content_type,
                title=content_type.label,
                text_content="",
                diagram_data=DiagramData(),
            )
            created.append(self._repo.create(item))
        return created

    def save_section(self, item: ContentItem) -> ContentItem:
        if not item.title.strip():
            item.title = item.content_type.label
        if item.id is None:
            return self._repo.create(item)
        return self._repo.update(item)
