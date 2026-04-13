import unittest
from unittest.mock import patch

from platypusbot.core.chatbot import Chatbot
from platypusbot.core.database import Database


class ChatbotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database(":memory:")
        self.bot = Chatbot(database=self.db, speaker=lambda text: True, listener=lambda: "hello")

    def tearDown(self) -> None:
        self.bot.close()

    def test_help_response(self) -> None:
        response = self.bot.generate_response("help")
        self.assertIn("weather", response.lower())
        self.assertIn("translate", response.lower())

    def test_math_response(self) -> None:
        self.assertEqual(self.bot.generate_response("solve 2 + 2"), "The result of 2 + 2 is 4.")

    def test_handle_message_saves_history(self) -> None:
        self.bot.handle_message("name")
        history = self.db.get_history(limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], "name")

    @patch("platypusbot.core.chatbot.get_weather", return_value="Weather in Boston: 20°C, clear sky, 50% humidity.")
    def test_weather_route(self, weather_mock) -> None:
        response = self.bot.generate_response("weather in Boston")
        self.assertIn("Boston", response)
        weather_mock.assert_called_once()

    @patch("platypusbot.core.chatbot.handle_realtime_query", return_value="Latest headlines:\n- Example story")
    def test_realtime_route(self, realtime_mock) -> None:
        response = self.bot.generate_response("latest news about AI")
        self.assertIn("Latest headlines", response)
        realtime_mock.assert_called()

    def test_translation_route(self) -> None:
        response = self.bot.generate_response("translate hola to english")
        self.assertIn("translation", response.lower())
        self.assertIn("hello", response.lower())

    def test_multilingual_alias_routing(self) -> None:
        with patch("platypusbot.core.chatbot.get_weather", return_value="Weather in Madrid: 22°C, clear sky, 40% humidity.") as weather_mock:
            response = self.bot.generate_response("clima en Madrid")
        self.assertIn("Madrid", response)
        weather_mock.assert_called_once()

    @patch("platypusbot.core.chatbot.llm_available", return_value=True)
    @patch("platypusbot.core.chatbot.generate_llm_response", return_value="Claro, aqui tienes una explicacion moderna.")
    def test_general_chat_uses_llm_when_available(self, llm_mock, available_mock) -> None:
        response = self.bot.generate_response("Explica la inteligencia artificial de forma sencilla.")
        self.assertIn("explicacion", response.lower())
        llm_mock.assert_called()
        available_mock.assert_called()

    @patch("platypusbot.core.chatbot.llm_available", return_value=True)
    @patch("platypusbot.core.chatbot.generate_llm_response", return_value="Machine learning is pattern recognition from data.")
    def test_explain_can_use_llm(self, llm_mock, available_mock) -> None:
        response = self.bot.generate_response("explain machine learning")
        self.assertIn("pattern recognition", response.lower())
        llm_mock.assert_called()
        available_mock.assert_called()

    def test_ui_status_contains_model_and_route(self) -> None:
        self.bot.generate_response("help")
        status = self.bot.get_ui_status()
        self.assertIn("route", status)
        self.assertIn("model", status)

    def test_stream_response_chunks_text(self) -> None:
        chunks = self.bot.stream_response("abcdefghijklmnop", chunk_size=5)
        self.assertEqual(chunks, ["abcde", "fghij", "klmno", "p"])


if __name__ == "__main__":
    unittest.main()
