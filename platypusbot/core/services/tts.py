from __future__ import annotations

from typing import Optional

try:
    import pyttsx3
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover - optional dependency
    sr = None

_engine: Optional[object] = None


def _get_engine() -> Optional[object]:
    global _engine
    if pyttsx3 is None:
        return None
    if _engine is None:
        try:
            _engine = pyttsx3.init()
        except Exception:
            _engine = None
    return _engine


def speak(text: str) -> bool:
    engine = _get_engine()
    if engine is None:
        return False
    try:
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        return False


def listen(timeout: int = 5) -> str:
    if sr is None:
        return "Voice input is unavailable because SpeechRecognition is not installed."

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=timeout)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Sorry, the speech recognition service is unavailable right now."
    except Exception as exc:
        return f"Voice input failed: {exc}"
