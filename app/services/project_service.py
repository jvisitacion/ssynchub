from __future__ import annotations

from db.repository.content_repository import ContentRepository
from db.repository.project_repository import ProjectRepository
from models.project import Project


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository | None = None,
        content_repository: ContentRepository | None = None,
    ) -> None:
        self._repo = repository or ProjectRepository()
        self._content_repo = content_repository or ContentRepository()

    def list_projects(self) -> list[Project]:
        return self._repo.get_all()

    def get(self, project_id: int) -> Project | None:
        return self._repo.get_by_id(project_id)

    def create(self, name: str = "New Project") -> Project:
        project = self._repo.create(name)
        assert project.id is not None
        from models.content import ContentItem, ContentType, DiagramData

        for content_type in ContentType:
            self._content_repo.create(
                ContentItem(
                    id=None,
                    project_id=project.id,
                    content_type=content_type,
                    title=content_type.label,
                    text_content="",
                    diagram_data=DiagramData(),
                )
            )
        return project

    def rename(self, project_id: int, name: str) -> Project:
        project = self._repo.rename(project_id, name)
        if project is None:
            raise ValueError(f"Project {project_id} not found")
        return project

    def delete(self, project_id: int) -> bool:
        return self._repo.delete(project_id)
