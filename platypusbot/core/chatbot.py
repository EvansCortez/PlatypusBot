from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from .database import Database
from .services.llm import generate_llm_response, llm_available, llm_status, preferred_model
from .services.realtime import handle_realtime_query, looks_like_realtime_query
from .services.tts import listen as default_listen
from .services.tts import speak as default_speak
from .services.translator import (
    SUPPORTED_LANGUAGES,
    detect_language,
    localize_response,
    normalize_language,
    translate_text,
)
from .services.weather import get_weather
from .services.wikipedia import search_wikipedia


@dataclass
class RouteDecision:
    intent: str
    normalized_input: str
    response_language: str
    use_llm: bool


class Chatbot:
    """Hybrid chatbot with service routing, optional LLM replies, and multilingual support."""

    GREETING_INPUTS = ("hello", "hi", "greetings", "hey", "what's up", "yo")
    GREETING_RESPONSES = ["Hi there!", "Hello!", "Hey!", "Greetings!", "Yo!"]
    FUN_FACTS = [
        "Platypuses are mammals that lay eggs.",
        "The longest concert on record lasted over 18 days.",
        "Japan has one of the highest vending machine densities in the world.",
    ]
    SCIENCE_FACTS = [
        "Water boils at 100 degrees Celsius at sea level.",
        "Earth takes about 365.25 days to orbit the Sun.",
        "The human brain contains roughly 86 billion neurons.",
    ]
    LANGUAGE_HINTS = {
        "spanish": "es",
        "español": "es",
        "french": "fr",
        "français": "fr",
        "german": "de",
        "deutsch": "de",
        "portuguese": "pt",
        "português": "pt",
        "italian": "it",
        "italiano": "it",
        "english": "en",
        "inglés": "en",
    }
    COMMAND_ALIASES = {
        "hola": "hello",
        "ayuda": "help",
        "clima": "weather",
        "tiempo": "weather",
        "noticias": "news",
        "hora": "time",
        "fecha": "date",
        "traducir": "translate",
        "resolver": "solve",
        "explica": "explain",
        "bonjour": "hello",
        "météo": "weather",
        "traduire": "translate",
        "nouvelles": "news",
        "heure": "time",
        "ciao": "hello",
        "meteo": "weather",
        "tradurre": "translate",
        "notizie": "news",
        "hallo": "hello",
        "wetter": "weather",
        "übersetzen": "translate",
        "nachrichten": "news",
    }
    CS_CONCEPTS = {
        "algorithm": "An algorithm is a step-by-step way to solve a problem.",
        "data structure": "A data structure is a way to organize data for efficient access and updates.",
        "machine learning": "Machine learning is a branch of AI where systems learn patterns from data.",
    }

    def __init__(
        self,
        database: Optional[Database] = None,
        speaker: Optional[Callable[[str], bool]] = None,
        listener: Optional[Callable[..., str]] = None,
    ) -> None:
        self.database = database or Database()
        self.speaker = speaker or default_speak
        self.listener = listener or default_listen
        self.conversations = [
            "Content strategy intern tasks.",
            "Chatbot that uses NLP",
            "Biases in Machine Learning.",
        ]
        self.last_detected_language = "en"
        self.last_route = "general"

    def greet(self, sentence: str) -> Optional[str]:
        lowered_words = sentence.lower().split()
        for word in lowered_words:
            if word.strip("?!.,") in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES)
        return None

    def solve_math(self, expression: str) -> str:
        try:
            allowed_names = {"abs": abs, "round": round}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result of {expression} is {result}."
        except Exception:
            return "I couldn't solve that math problem. Please check the expression and try again."

    def explain_concept(self, concept: str) -> str:
        normalized = concept.strip().lower()
        if normalized in self.CS_CONCEPTS:
            return self.CS_CONCEPTS[normalized]
        choices = ", ".join(sorted(self.CS_CONCEPTS))
        return f"I don't have a saved explanation for that yet. Try one of these: {choices}"

    def analyze_sentiment(self, text: str) -> str:
        lowered = text.lower()
        positive_words = {"love", "great", "awesome", "amazing", "good", "happy"}
        negative_words = {"hate", "bad", "terrible", "awful", "sad", "angry"}
        positive_hits = sum(word in lowered for word in positive_words)
        negative_hits = sum(word in lowered for word in negative_words)
        if positive_hits > negative_hits:
            return "The sentiment sounds positive."
        if negative_hits > positive_hits:
            return "The sentiment sounds negative."
        return "The sentiment sounds neutral."

    def classify_text(self, text: str, training_data: Iterable[str], labels: Iterable[str]) -> str:
        label_scores = {}
        for sample, label in zip(training_data, labels):
            sample_words = set(sample.lower().split())
            overlap = len(sample_words.intersection(text.lower().split()))
            label_scores[label] = label_scores.get(label, 0) + overlap
        if not label_scores:
            return "unknown"
        return max(label_scores, key=label_scores.get)

    def get_help_text(self) -> str:
        return (
            "I can help with greetings, live weather, Wikipedia, current time and headlines, math, "
            "facts, translation, multilingual chat, sentiment checks, voice mode, and an optional LLM chat layer. "
            "Try 'weather in Boston', 'latest news about AI', 'translate hello to Spanish', or 'Explain neural networks in French'."
        )

    def _normalize_text(self, text: str) -> str:
        lowered = text.lower()
        for original, replacement in self.COMMAND_ALIASES.items():
            lowered = re.sub(rf"\b{re.escape(original)}\b", replacement, lowered)
        return lowered

    def _extract_requested_language(self, text: str) -> Optional[str]:
        lowered = text.lower()
        for hint, code in self.LANGUAGE_HINTS.items():
            if hint in lowered:
                return code
        language_match = re.search(r"\bto\s+([a-zA-ZÀ-ÿ]+)\b", lowered)
        if language_match:
            return normalize_language(language_match.group(1))
        return None

    def _history_context(self, limit: int = 5) -> list[tuple[str, str, str]]:
        history = self.database.get_history(limit=limit)
        return list(reversed(history))

    def _generate_with_llm(self, user_input: str, response_language: str, preface: Optional[str] = None) -> Optional[str]:
        return generate_llm_response(
            user_input=user_input,
            history=self._history_context(),
            response_language=response_language,
            preface=preface,
        )

    def route_request(self, user_input: str) -> RouteDecision:
        detected_language = detect_language(user_input)
        self.last_detected_language = detected_language
        normalized_input = self._normalize_text(user_input.strip())
        requested_language = self._extract_requested_language(normalized_input)
        response_language = requested_language or detected_language or "en"
        llm_enabled = llm_available()

        if not normalized_input:
            return RouteDecision("empty", normalized_input, response_language, False)
        if normalized_input.startswith("translate"):
            return RouteDecision("translate", normalized_input, response_language, llm_enabled)
        if looks_like_realtime_query(normalized_input):
            return RouteDecision("realtime", normalized_input, response_language, False)
        if "weather" in normalized_input:
            return RouteDecision("weather", normalized_input, response_language, False)
        if normalized_input.startswith("wikipedia"):
            return RouteDecision("wikipedia", normalized_input, response_language, llm_enabled)
        if normalized_input.startswith("sentiment"):
            return RouteDecision("sentiment", normalized_input, response_language, False)
        if normalized_input.startswith("solve"):
            return RouteDecision("solve", normalized_input, response_language, False)
        if normalized_input.startswith("explain"):
            return RouteDecision("explain", normalized_input, response_language, llm_enabled)
        if normalized_input.startswith("classify"):
            return RouteDecision("classify", normalized_input, response_language, False)
        return RouteDecision("general", normalized_input, response_language, llm_enabled)

    def _handle_translation_intent(self, raw_input: str, normalized_input: str) -> str:
        target_language = self._extract_requested_language(normalized_input) or "en"
        match = re.search(r"translate\s+(.+?)\s+to\s+[a-zA-ZÀ-ÿ]+$", raw_input, re.IGNORECASE)
        if not match:
            return "Try 'translate hello to Spanish' or 'translate bonjour to English'."

        text_to_translate = match.group(1).strip(" '\"")
        llm_translation = self._generate_with_llm(
            user_input=f"Translate this text to {SUPPORTED_LANGUAGES.get(target_language, target_language)}: {text_to_translate}",
            response_language=target_language,
        )
        if llm_translation:
            language_name = SUPPORTED_LANGUAGES.get(target_language, target_language)
            return f"Translation ({language_name}): {llm_translation}"

        result = translate_text(text_to_translate, target_language=target_language)
        language_name = SUPPORTED_LANGUAGES.get(result.target_language, result.target_language)
        return (
            f"Translation ({result.source_language} -> {language_name}): {result.text}"
            if result.text
            else "I couldn't translate that text."
        )

    def _localize_if_needed(self, response: str, response_language: str) -> str:
        if response_language == "en":
            return response
        return localize_response(response, response_language)

    def get_ui_status(self) -> dict[str, str]:
        return {
            "language": SUPPORTED_LANGUAGES.get(self.last_detected_language, self.last_detected_language),
            "route": self.last_route,
            "model": preferred_model(),
            "llm": llm_status(),
        }

    def get_preferences(self) -> dict[str, str]:
        return self.database.get_preferences()

    def set_preference(self, key: str, value: str) -> None:
        self.database.set_preference(key, value)

    def stream_response(self, text: str, chunk_size: int = 18) -> list[str]:
        if not text:
            return [""]
        return [text[index : index + chunk_size] for index in range(0, len(text), chunk_size)]

    def generate_response(self, user_input: str) -> str:
        raw_input = user_input.strip()
        decision = self.route_request(raw_input)
        normalized_input = decision.normalized_input
        response_language = decision.response_language
        self.last_route = decision.intent

        if decision.intent == "empty":
            return self._localize_if_needed(
                "I didn't catch anything there. Try asking a question or type 'help'.",
                response_language,
            )

        if decision.intent == "general":
            greeting = self.greet(normalized_input)
            if greeting:
                return self._localize_if_needed(greeting, response_language)

        lowered = normalized_input.lower()

        if "how are you" in lowered:
            return self._localize_if_needed(
                "I'm doing great and ready to help. What are we working on today?",
                response_language,
            )
        if "study" in lowered:
            return self._localize_if_needed(
                "I can help you study with explanations, quick facts, and practice prompts. Pick a topic and we can dive in.",
                response_language,
            )
        if "example" in lowered:
            return self._localize_if_needed(
                "Try asking 'solve 12 * 8', 'weather in Atlanta', 'latest news about robotics', 'wikipedia platypus', or 'Explain machine learning in Spanish'.",
                response_language,
            )
        if "capabilities" in lowered:
            return self._localize_if_needed(
                "I can chat, answer simple questions, look up live weather, current headlines and time, search Wikipedia, save history, translate supported languages, and use an OpenAI-backed chat layer when configured.",
                response_language,
            )
        if "limitations" in lowered:
            return self._localize_if_needed(
                "I still rely on external services for live data and deeper multilingual conversations, and I can fall back to simpler rules when those services are unavailable.",
                response_language,
            )
        if any(convo.lower() in lowered for convo in self.conversations):
            for convo in self.conversations:
                if convo.lower() in lowered:
                    return self._localize_if_needed(
                        f"Let's talk about '{convo}'. What would you like to explore about it?",
                        response_language,
                    )
        if "unlimited" in lowered or "everything" in lowered:
            return self._localize_if_needed(
                "I handle chat, math, facts, translation, multilingual prompts, live weather, headlines, time, Wikipedia, sentiment, persistent history, and optional LLM responses.",
                response_language,
            )
        if any(term in lowered for term in ("formatting", "markdown", "display text differently")):
            return self._localize_if_needed(
                "You can use markdown like # headings, **bold**, *italic*, `code`, lists, links, and blockquotes.",
                response_language,
            )
        if decision.intent == "translate":
            return self._handle_translation_intent(raw_input, normalized_input)
        if decision.intent == "realtime":
            response = handle_realtime_query(normalized_input)
            if response is not None:
                return self._localize_if_needed(response, response_language)
        if decision.intent == "classify":
            text_to_classify = raw_input[8:].strip()
            if not text_to_classify:
                return self._localize_if_needed("Please provide text after 'classify'.", response_language)
            training_data = ["I love this", "This is terrible", "Amazing work", "Worst ever"]
            labels = ["positive", "negative", "positive", "negative"]
            return self._localize_if_needed(
                f"I classify this as: {self.classify_text(text_to_classify, training_data, labels)}",
                response_language,
            )
        if decision.intent == "weather":
            city = lowered.replace("weather", "").replace("in", "").strip()
            response = get_weather(city) if city else "Please tell me which city you want the weather for."
            return self._localize_if_needed(response, response_language)
        if decision.intent == "sentiment":
            text = raw_input[len("sentiment") :].strip()
            response = self.analyze_sentiment(text) if text else "Please provide text after 'sentiment'."
            return self._localize_if_needed(response, response_language)
        if decision.intent == "wikipedia":
            query = raw_input[len("wikipedia") :].strip()
            response = search_wikipedia(query) if query else "Tell me what topic to search on Wikipedia."
            if decision.use_llm and query:
                llm_response = self._generate_with_llm(
                    user_input=raw_input,
                    response_language=response_language,
                    preface=f"Wikipedia summary:\n{response}",
                )
                if llm_response:
                    return llm_response
            return self._localize_if_needed(response, response_language)
        if decision.intent == "solve":
            expression = raw_input[len("solve") :].strip()
            response = self.solve_math(expression) if expression else "Please provide a math expression after 'solve'."
            return self._localize_if_needed(response, response_language)
        if "fun fact" in lowered or "tell me something" in lowered:
            return self._localize_if_needed(random.choice(self.FUN_FACTS), response_language)
        if "science fact" in lowered:
            return self._localize_if_needed(random.choice(self.SCIENCE_FACTS), response_language)
        if decision.intent == "explain":
            concept_response = self.explain_concept(raw_input[len("explain") :].strip())
            if decision.use_llm:
                llm_response = self._generate_with_llm(
                    user_input=raw_input,
                    response_language=response_language,
                    preface=f"Starter concept note:\n{concept_response}",
                )
                if llm_response:
                    return llm_response
            return self._localize_if_needed(concept_response, response_language)
        if "name" in lowered:
            return self._localize_if_needed(
                "I'm PlatypusBot, your helpful cross-interface chatbot.",
                response_language,
            )
        if "help" in lowered:
            return self._localize_if_needed(self.get_help_text(), response_language)
        if decision.use_llm:
            llm_response = self._generate_with_llm(raw_input, response_language=response_language)
            if llm_response:
                return llm_response
        return self._localize_if_needed(
            "I'm not sure how to respond to that yet. Type 'help' to see what I can do.",
            response_language,
        )

    def handle_message(self, user_input: str) -> str:
        response = self.generate_response(user_input)
        self.database.save_chat_history(user_input, response)
        return response

    def speak(self, text: str) -> bool:
        return self.speaker(text)

    def listen(self) -> str:
        return self.listener()

    def close(self) -> None:
        self.database.close()
