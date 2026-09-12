"""Abstract Repository — defines the CRUD contract shared by all repositories."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_all(self) -> list[T]:
        ...

    @abstractmethod
    def get_by_id(self, item_id: int) -> T | None:
        ...

    @abstractmethod
    def create(self, item: T) -> T:
        ...

    @abstractmethod
    def update(self, item: T) -> T:
        ...

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        ...
