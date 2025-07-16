# You need to install nltk to use this module.
# Run this in your terminal:
# pip install nltk

import random
import logging
from datetime import datetime
import nltk

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import ChatDatabase
from core.nlp_processor import NLPProcessor
from core.llm_integration import LLMHandler
from core.services.weather import WeatherService
from core.services.wikipedia import WikipediaService
from core.services.tts import TextToSpeechService

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, config):
        self.config = config
        self.db = ChatDatabase(config.DB_PATH)
        self.nlp = NLPProcessor()
        self.llm = LLMHandler(config.LLM_MODEL)
        self.services = {
            "weather": WeatherService(config.WEATHER_API_KEY),
            "wikipedia": WikipediaService(),
            "tts": TextToSpeechService()
        }
        self.conversation_starters = [
            "Content strategy intern tasks.",
            "Chatbot that uses NLP",
            "Biases in Machine Learning."
        ]
        self.greeting_responses = [
            "Hi there!", "Hello!", "Hey!", "Greetings!"
        ]
        self.fun_facts = [
            "The world's longest concert lasted 453 hours.",
            "Africa is the only continent in all four hemispheres."
        ]
        self.cs_concepts = {
            "algorithm": "An algorithm is a step-by-step procedure for solving a problem.",
            "data structure": "A way of organizing and storing data efficiently."
        }

        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        try:
            nltk.data.find('chunkers/maxent_ne_chunker')
        except LookupError:
            nltk.download('maxent_ne_chunker')
        try:
            nltk.data.find('corpora/words')
        except LookupError:
            nltk.download('words')
        try:
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')

    def _get_context(self, conversation_id):
        if not conversation_id:
            return []
        return self.db.get_conversation_messages(conversation_id)

    def _build_prompt(self, user_input, context):
        prompt = "You are PlatypusBot, a helpful AI assistant.\n"
        for msg in context[-5:]:
            prompt += f"{msg['sender']}: {msg['content']}\n"
        prompt += f"user: {user_input}\nassistant:"
        return prompt

    def process_message(self, user_input, conversation_id=None):
        try:
            if any(greet in user_input.lower() for greet in ["hi", "hello", "hey"]):
                return {
                    "response": random.choice(self.greeting_responses),
                    "conversation_id": conversation_id
                }

            context = self._get_context(conversation_id)
            nlp_result = self.nlp.process_input(user_input, context)

            if nlp_result["intent"] == "weather":
                response = self.services["weather"].get_weather(
                    nlp_result["entities"].get("location", ""))
            elif nlp_result["intent"] == "wikipedia":
                response = self.services["wikipedia"].search(
                    nlp_result["entities"].get("topic", ""))
            elif "fun fact" in user_input.lower():
                response = random.choice(self.fun_facts)
            elif "explain" in user_input.lower():
                concept = user_input.replace("explain", "").strip()
                response = self.cs_concepts.get(
                    concept, "I don't have information on that concept.")
            else:
                prompt = self._build_prompt(user_input, context)
                response = self.llm.generate(prompt)

            if not conversation_id:
                conversation_id = self.db.create_conversation("New Chat")
            self.db.save_message(conversation_id, "user", user_input)
            self.db.save_message(conversation_id, "bot", response)

            return {
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "error": "Sorry, something went wrong.",
                "details": str(e)
            }

if __name__ == "__main__":
    print("PlatypusBot core.chatbot module loaded successfully.")
    # Optionally, add demo/test code here
    # Example:
    # from config import Config
    # bot = Chatbot(Config)
    # print(bot.process_message("hello"))
