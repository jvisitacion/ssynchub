"""In-memory draft store — one draft per project section."""

from __future__ import annotations

from copy import deepcopy

from models.content import ContentItem, ContentType

DraftKey = tuple[int, ContentType]


class DraftStore:
    def __init__(self) -> None:
        self._drafts: dict[DraftKey, ContentItem] = {}
        self._dirty: set[DraftKey] = set()

    @staticmethod
    def key(project_id: int, content_type: ContentType) -> DraftKey:
        return (project_id, content_type)

    def stash(self, draft_key: DraftKey, item: ContentItem, *, is_dirty: bool) -> None:
        self._drafts[draft_key] = deepcopy(item)
        if is_dirty:
            self._dirty.add(draft_key)
        else:
            self._dirty.discard(draft_key)

    def get(self, draft_key: DraftKey) -> ContentItem | None:
        stored = self._drafts.get(draft_key)
        return deepcopy(stored) if stored else None

    def is_dirty(self, draft_key: DraftKey) -> bool:
        return draft_key in self._dirty

    def remove(self, draft_key: DraftKey) -> None:
        self._drafts.pop(draft_key, None)
        self._dirty.discard(draft_key)

    def has_dirty_in_project(self, project_id: int) -> bool:
        return any(key[0] == project_id for key in self._dirty)

    def clear_project(self, project_id: int) -> None:
        keys = [key for key in self._drafts if key[0] == project_id]
        for key in keys:
            self.remove(key)
