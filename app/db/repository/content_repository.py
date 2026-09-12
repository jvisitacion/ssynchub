"""Repository Pattern — isolates SQL from the rest of the application."""

from __future__ import annotations

import json

from db.connection import DatabaseConnection
from db.repository.base_repository import BaseRepository
from models.content import ContentItem, ContentType, DiagramData


class ContentRepository(BaseRepository[ContentItem]):
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def get_by_project_and_type(
        self, project_id: int, content_type: ContentType
    ) -> ContentItem | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, project_id, content_type, title, text_content, diagram_data,
                       attachment_path, created_at, updated_at
                FROM content_items
                WHERE project_id = %s AND content_type = %s
                """,
                (project_id, content_type.value),
            )
            row = cur.fetchone()
            return self._row_to_item(row) if row else None

    def get_all_by_project(self, project_id: int) -> list[ContentItem]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, project_id, content_type, title, text_content, diagram_data,
                       attachment_path, created_at, updated_at
                FROM content_items
                WHERE project_id = %s
                ORDER BY content_type
                """,
                (project_id,),
            )
            return [self._row_to_item(row) for row in cur.fetchall()]

    def get_all(self) -> list[ContentItem]:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, project_id, content_type, title, text_content, diagram_data,
                       attachment_path, created_at, updated_at
                FROM content_items
                ORDER BY updated_at DESC
                """
            )
            return [self._row_to_item(row) for row in cur.fetchall()]

    def get_by_id(self, item_id: int) -> ContentItem | None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                SELECT id, project_id, content_type, title, text_content, diagram_data,
                       attachment_path, created_at, updated_at
                FROM content_items
                WHERE id = %s
                """,
                (item_id,),
            )
            row = cur.fetchone()
            return self._row_to_item(row) if row else None

    def create(self, item: ContentItem) -> ContentItem:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO content_items
                    (project_id, content_type, title, text_content, diagram_data, attachment_path)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at, updated_at
                """,
                (
                    item.project_id,
                    item.content_type.value,
                    item.title,
                    item.text_content,
                    json.dumps(item.diagram_data.to_dict()),
                    item.attachment_path,
                ),
            )
            row = cur.fetchone()
            item.id = row[0]
            item.created_at = row[1]
            item.updated_at = row[2]
            return item

    def update(self, item: ContentItem) -> ContentItem:
        if item.id is None:
            raise ValueError("Cannot update item without id")
        with self._db.cursor() as cur:
            cur.execute(
                """
                UPDATE content_items
                SET title = %s,
                    text_content = %s,
                    diagram_data = %s,
                    attachment_path = %s,
                    updated_at = NOW()
                WHERE id = %s
                RETURNING updated_at
                """,
                (
                    item.title,
                    item.text_content,
                    json.dumps(item.diagram_data.to_dict()),
                    item.attachment_path,
                    item.id,
                ),
            )
            item.updated_at = cur.fetchone()[0]
            return item

    def delete(self, item_id: int) -> bool:
        with self._db.cursor() as cur:
            cur.execute("DELETE FROM content_items WHERE id = %s", (item_id,))
            return cur.rowcount > 0

    @staticmethod
    def _row_to_item(row: tuple) -> ContentItem:
        diagram_raw = row[5]
        if isinstance(diagram_raw, str):
            diagram_raw = json.loads(diagram_raw)
        return ContentItem(
            id=row[0],
            project_id=row[1],
            content_type=ContentType(row[2]),
            title=row[3],
            text_content=row[4] or "",
            diagram_data=DiagramData.from_dict(diagram_raw),
            attachment_path=row[6],
            created_at=row[7],
            updated_at=row[8],
        )
