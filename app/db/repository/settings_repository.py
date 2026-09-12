from __future__ import annotations

from db.connection import DatabaseConnection


class SettingsRepository:
    def __init__(self, db: DatabaseConnection | None = None) -> None:
        self._db = db or DatabaseConnection()

    def get(self, key: str, default: str = "") -> str:
        with self._db.cursor() as cur:
            cur.execute(
                "SELECT setting_value FROM app_settings WHERE setting_key = %s",
                (key,),
            )
            row = cur.fetchone()
            return row[0] if row else default

    def set(self, key: str, value: str) -> None:
        with self._db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO app_settings (setting_key, setting_value, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (setting_key)
                DO UPDATE SET setting_value = EXCLUDED.setting_value,
                              updated_at = NOW()
                """,
                (key, value),
            )
