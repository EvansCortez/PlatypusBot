from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Optional

import requests


SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "pt": "portuguese",
    "it": "italian",
}

LANGUAGE_NAME_TO_CODE = {name: code for code, name in SUPPORTED_LANGUAGES.items()}
LANGUAGE_NAME_TO_CODE.update(
    {
        "inglés": "en",
        "español": "es",
        "francés": "fr",
        "alemán": "de",
        "portugués": "pt",
        "italiano": "it",
    }
)

LANGUAGE_MARKERS = {
    "es": {"hola", "clima", "tiempo", "traducir", "gracias", "por favor", "noticias", "hoy"},
    "fr": {"bonjour", "météo", "traduire", "merci", "heure", "aujourd'hui", "nouvelles"},
    "de": {"hallo", "wetter", "übersetzen", "danke", "uhrzeit", "nachrichten", "heute"},
    "pt": {"ola", "tempo", "traduzir", "obrigado", "noticias", "hoje"},
    "it": {"ciao", "meteo", "tradurre", "grazie", "notizie", "oggi"},
}

PHRASEBOOK = {
    ("es", "en"): {
        "hola": "hello",
        "ayuda": "help",
        "clima": "weather",
        "tiempo": "weather",
        "noticias": "news",
        "hora": "time",
        "fecha": "date",
        "wikipedia": "wikipedia",
        "traducir": "translate",
        "explica": "explain",
        "resolver": "solve",
        "sentimiento": "sentiment",
    },
    ("fr", "en"): {
        "bonjour": "hello",
        "aide": "help",
        "météo": "weather",
        "nouvelles": "news",
        "heure": "time",
        "date": "date",
        "traduire": "translate",
        "expliquer": "explain",
        "résoudre": "solve",
        "sentiment": "sentiment",
    },
    ("de", "en"): {
        "hallo": "hello",
        "hilfe": "help",
        "wetter": "weather",
        "nachrichten": "news",
        "uhrzeit": "time",
        "datum": "date",
        "übersetzen": "translate",
        "erkläre": "explain",
        "lösen": "solve",
        "stimmung": "sentiment",
    },
    ("pt", "en"): {
        "ola": "hello",
        "ajuda": "help",
        "tempo": "weather",
        "noticias": "news",
        "hora": "time",
        "data": "date",
        "traduzir": "translate",
        "explicar": "explain",
        "resolver": "solve",
        "sentimento": "sentiment",
    },
    ("it", "en"): {
        "ciao": "hello",
        "aiuto": "help",
        "meteo": "weather",
        "notizie": "news",
        "ora": "time",
        "data": "date",
        "tradurre": "translate",
        "spiega": "explain",
        "risolvi": "solve",
        "sentimento": "sentiment",
    },
}


@dataclass
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    provider: str


def detect_language(text: str) -> str:
    lowered = text.lower()
    for code, markers in LANGUAGE_MARKERS.items():
        if any(marker in lowered for marker in markers):
            return code
    if re.search(r"[¿¡ñáéíóú]", lowered):
        return "es"
    if re.search(r"[àâçèéêëîïôûùüÿœ]", lowered):
        return "fr"
    if re.search(r"[äöüß]", lowered):
        return "de"
    return "en"


def normalize_language(value: str) -> Optional[str]:
    lowered = value.strip().lower()
    if lowered in SUPPORTED_LANGUAGES:
        return lowered
    return LANGUAGE_NAME_TO_CODE.get(lowered)


def _translate_via_api(text: str, source_language: str, target_language: str) -> Optional[TranslationResult]:
    base_url = os.getenv("LIBRETRANSLATE_URL")
    if not base_url:
        return None

    payload = {
        "q": text,
        "source": source_language,
        "target": target_language,
        "format": "text",
    }
    api_key = os.getenv("LIBRETRANSLATE_API_KEY")
    if api_key:
        payload["api_key"] = api_key

    try:
        response = requests.post(base_url.rstrip("/") + "/translate", json=payload, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        return None

    translated_text = response.json().get("translatedText")
    if not translated_text:
        return None
    return TranslationResult(
        text=translated_text,
        source_language=source_language,
        target_language=target_language,
        provider="libretranslate",
    )


def _translate_via_phrasebook(text: str, source_language: str, target_language: str) -> Optional[TranslationResult]:
    translations = PHRASEBOOK.get((source_language, target_language))
    if not translations:
        return None

    translated_tokens = []
    for token in text.split():
        cleaned = re.sub(r"[^\wÀ-ÿ'-]", "", token.lower())
        replacement = translations.get(cleaned, token)
        translated_tokens.append(replacement)

    return TranslationResult(
        text=" ".join(translated_tokens),
        source_language=source_language,
        target_language=target_language,
        provider="phrasebook",
    )


def translate_text(
    text: str,
    target_language: str = "en",
    source_language: Optional[str] = None,
) -> TranslationResult:
    source = source_language or detect_language(text)
    target = normalize_language(target_language) or "en"
    if source == target:
        return TranslationResult(text=text, source_language=source, target_language=target, provider="identity")

    api_result = _translate_via_api(text, source, target)
    if api_result is not None:
        return api_result

    phrasebook_result = _translate_via_phrasebook(text, source, target)
    if phrasebook_result is not None:
        return phrasebook_result

    return TranslationResult(
        text=text,
        source_language=source,
        target_language=target,
        provider="fallback",
    )


def localize_response(text: str, target_language: str) -> str:
    result = translate_text(text, target_language=target_language, source_language="en")
    if result.provider == "fallback" and target_language != "en":
        language_name = SUPPORTED_LANGUAGES.get(target_language, target_language)
        return f"{text}\n\nTranslation note: richer {language_name} responses are available when LibreTranslate is configured."
    return result.text
