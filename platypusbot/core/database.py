from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


class Database:
    """Small SQLite wrapper for storing conversation history."""

    def __init__(self, db_path: str | Path = "chat_history.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.setup_database()

    def setup_database(self) -> None:
        with self.db_conn:
            self.db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT NOT NULL,
                    response TEXT NOT NULL
                )
                """
            )
            self.db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

    def save_chat_history(self, user_input: str, response: str) -> None:
        with self.db_conn:
            self.db_conn.execute(
                "INSERT INTO history (user_input, response) VALUES (?, ?)",
                (user_input, response),
            )

    def get_history(self, limit: int = 10) -> List[Tuple[str, str, str]]:
        cursor = self.db_conn.cursor()
        cursor.execute(
            """
            SELECT user_input, response, timestamp
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()

    def set_preference(self, key: str, value: str) -> None:
        with self.db_conn:
            self.db_conn.execute(
                """
                INSERT INTO preferences (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row is None:
            return default
        return row[0]

    def get_preferences(self) -> dict[str, str]:
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT key, value FROM preferences")
        return {key: value for key, value in cursor.fetchall()}

    def close(self) -> None:
        self.db_conn.close()
