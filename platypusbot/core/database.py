import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ChatDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._initialize_db()

    @contextmanager
    def _cursor(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"DB error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_db(self):
        with self._cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    sender TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            """)

    def create_conversation(self, title):
        import uuid
        conv_id = str(uuid.uuid4())
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO conversations (id, title) VALUES (?, ?)",
                (conv_id, title)
            )
        return conv_id

    def save_message(self, conversation_id, sender, content):
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES (?, ?, ?)",
                (conversation_id, sender, content)
            )

    def get_conversation_messages(self, conversation_id):
        with self._cursor() as cur:
            cur.execute(
                "SELECT sender, content, timestamp FROM messages WHERE conversation_id=? ORDER BY timestamp ASC",
                (conversation_id,)
            )
            return [{"sender": s, "content": c, "timestamp": t} for s, c, t in cur.fetchall()]

    def get_conversations(self):
        with self._cursor() as cur:
            cur.execute(
                "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC"
            )
            return [{"id": i, "title": t, "created_at": c} for i, t, c in cur.fetchall()]
