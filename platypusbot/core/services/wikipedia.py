from __future__ import annotations

import wikipedia


def search_wikipedia(query: str) -> str:
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as exc:
        options = ", ".join(exc.options[:3])
        return f"Multiple Wikipedia results matched that topic. Try one of these: {options}"
    except wikipedia.exceptions.PageError:
        return "I couldn't find a Wikipedia page for that topic."
    except Exception:
        return "Wikipedia is unavailable right now. Please try again in a bit."
