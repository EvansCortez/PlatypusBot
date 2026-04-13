import unittest

from platypusbot.core.database import Database


class DatabaseTests(unittest.TestCase):
    def test_save_and_fetch_history(self) -> None:
        db = Database(":memory:")
        try:
            db.save_chat_history("hello", "Hi there!")
            history = db.get_history(limit=1)
            self.assertEqual(history[0][0], "hello")
            self.assertEqual(history[0][1], "Hi there!")
        finally:
            db.close()

    def test_preferences_round_trip(self) -> None:
        db = Database(":memory:")
        try:
            db.set_preference("language", "fr")
            self.assertEqual(db.get_preference("language"), "fr")
            self.assertEqual(db.get_preferences()["language"], "fr")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
