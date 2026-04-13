from __future__ import annotations

import os
from typing import List, Optional, Sequence, Tuple

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None


HistoryItem = Tuple[str, str, str]


def llm_available() -> bool:
    return OpenAI is not None and bool(os.getenv("OPENAI_API_KEY"))


def llm_status() -> str:
    if OpenAI is None:
        return "OpenAI SDK not installed"
    if not os.getenv("OPENAI_API_KEY"):
        return "OPENAI_API_KEY missing"
    return "Connected"


def preferred_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5-mini")


def _format_history(history: Sequence[HistoryItem]) -> str:
    lines: List[str] = []
    for user_input, response, timestamp in history:
        lines.append(f"[{timestamp}] User: {user_input}")
        lines.append(f"[{timestamp}] PlatypusBot: {response}")
    return "\n".join(lines)


def _build_instructions(response_language: str, realtime_enabled: bool) -> str:
    language_clause = (
        f"Reply in {response_language} unless the user explicitly asks for another language."
        if response_language != "en"
        else "Reply in English unless the user explicitly asks for another language."
    )
    realtime_clause = (
        "If the user asks for live facts like weather, breaking news, or current time, keep the answer concise and defer to the dedicated live-data tools when needed."
        if not realtime_enabled
        else "When live-data context is provided, incorporate it naturally and do not invent newer facts."
    )
    return (
        "You are PlatypusBot, a friendly desktop assistant. "
        "Give concise, useful answers with a modern chat tone. "
        f"{language_clause} "
        f"{realtime_clause}"
    )


def generate_llm_response(
    user_input: str,
    history: Sequence[HistoryItem] | None = None,
    response_language: str = "en",
    preface: Optional[str] = None,
) -> Optional[str]:
    if not llm_available():
        return None

    client = OpenAI()
    prompt_parts: List[str] = []
    if history:
        prompt_parts.append("Conversation history:\n" + _format_history(history))
    if preface:
        prompt_parts.append("Useful context:\n" + preface)
    prompt_parts.append("User message:\n" + user_input)
    prompt = "\n\n".join(prompt_parts)

    try:
        response = client.responses.create(
            model=preferred_model(),
            instructions=_build_instructions(response_language=response_language, realtime_enabled=bool(preface)),
            input=prompt,
        )
    except Exception:
        return None

    text = getattr(response, "output_text", None)
    if text:
        return text.strip()
    return None
