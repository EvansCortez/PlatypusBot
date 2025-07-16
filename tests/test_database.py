import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import ChatDatabase

def test_database(tmp_path):
    db_path = tmp_path / "test.db"
    db = ChatDatabase(str(db_path))
    conv_id = db.create_conversation("Test Conversation")
    db.save_message(conv_id, "user", "Hi")
    db.save_message(conv_id, "bot", "Hello!")
    messages = db.get_conversation_messages(conv_id)
    assert len(messages) == 2
    assert messages[0]["sender"] == "user"
