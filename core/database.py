# core/database.py

from contextlib import contextmanager
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ChatDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._initialize_db()

    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_db(self):
        with self._get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    sender TEXT CHECK(sender IN ('user', 'bot')),
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            """)

    def save_message(self, conversation_id, sender, content):
        with self._get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
                (conversation_id, sender, content)
            )

    def create_conversation(self, title):
        with self._get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations (title) VALUES (?)",
                (title,)
            )
            return cursor.lastrowid

    def get_conversation_messages(self, conversation_id):
        with self._get_cursor() as cursor:
            cursor.execute(
                "SELECT sender, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
                (conversation_id,)
            )
            return cursor.fetchall()