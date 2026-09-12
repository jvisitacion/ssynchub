"""Factory + context manager for PostgreSQL connections."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as PgConnection

from config.settings import Settings


class DatabaseConnection:
    """Factory that hands out psycopg2 connections using app settings."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def connect(self) -> PgConnection:
        return psycopg2.connect(self._settings.db.dsn)

    @contextmanager
    def cursor(self) -> Generator:
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        sql = schema_path.read_text(encoding="utf-8")
        with self.cursor() as cur:
            cur.execute(sql)

    def ping(self) -> bool:
        try:
            with self.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception:
            return False
