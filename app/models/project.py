"""Project domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: int | None
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
