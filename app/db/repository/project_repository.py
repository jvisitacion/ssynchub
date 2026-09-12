from __future__ import annotations

from db.connection import DatabaseConnection
from models.project import Project


class ProjectRepository:
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def get_all(self) -> list[Project]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, created_at, updated_at
                FROM projects
                ORDER BY updated_at DESC, name ASC
                """
            )
            return [self._row_to_project(row) for row in cur.fetchall()]

    def get_by_id(self, project_id: int) -> Project | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, created_at, updated_at
                FROM projects
                WHERE id = %s
                """,
                (project_id,),
            )
            row = cur.fetchone()
            return self._row_to_project(row) if row else None

    def create(self, name: str) -> Project:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO projects (name)
                VALUES (%s)
                RETURNING id, created_at, updated_at
                """,
                (name.strip() or "Untitled Project",),
            )
            row = cur.fetchone()
            return Project(id=row[0], name=name.strip() or "Untitled Project", created_at=row[1], updated_at=row[2])

    def rename(self, project_id: int, name: str) -> Project | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                UPDATE projects
                SET name = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, name, created_at, updated_at
                """,
                (name.strip() or "Untitled Project", project_id),
            )
            row = cur.fetchone()
            return self._row_to_project(row) if row else None

    def delete(self, project_id: int) -> bool:
        with self._db.cursor() as cur:
            cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
            return cur.rowcount > 0

    @staticmethod
    def _row_to_project(row: tuple) -> Project:
        return Project(id=row[0], name=row[1], created_at=row[2], updated_at=row[3])
