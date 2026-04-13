from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import requests


TIMEZONE_ALIASES = {
    "new york": "America/New_York",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    "madrid": "Europe/Madrid",
}


def get_current_time(location: Optional[str] = None) -> str:
    timezone_name = TIMEZONE_ALIASES.get((location or "").strip().lower(), "America/New_York")
    now = datetime.now(ZoneInfo(timezone_name))
    city = location.title() if location else "New York"
    return f"The current time in {city} is {now.strftime('%I:%M %p on %A, %B %d, %Y')}."


def get_current_date() -> str:
    today = datetime.now(ZoneInfo("America/New_York"))
    return f"Today's date is {today.strftime('%A, %B %d, %Y')}."


def get_latest_headlines(topic: Optional[str] = None) -> str:
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Live news is available when NEWS_API_KEY is configured."

    params = {
        "apiKey": api_key,
        "language": "en",
        "pageSize": 3,
        "sortBy": "publishedAt",
    }
    endpoint = "https://newsapi.org/v2/top-headlines"
    if topic:
        endpoint = "https://newsapi.org/v2/everything"
        params["q"] = topic
    else:
        params["country"] = "us"

    try:
        response = requests.get(endpoint, params=params, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        return "I couldn't reach the live news service right now."

    articles = response.json().get("articles", [])
    if not articles:
        return "I couldn't find any live headlines for that topic right now."

    lines = []
    for article in articles[:3]:
        title = article.get("title", "Untitled")
        source = article.get("source", {}).get("name", "Unknown source")
        lines.append(f"- {title} ({source})")
    if topic:
        return "Latest headlines about " + topic + ":\n" + "\n".join(lines)
    return "Latest headlines:\n" + "\n".join(lines)


def looks_like_realtime_query(query: str) -> bool:
    lowered = query.lower().strip()
    return bool(re.search(r"\b(time|current time|what time|date|today|what day|news|headlines|latest)\b", lowered))


def handle_realtime_query(query: str) -> Optional[str]:
    lowered = query.lower().strip()

    if re.search(r"\b(time|current time|what time)\b", lowered):
        location_match = re.search(r"\b(?:in|for)\s+([a-zA-Z\s]+)$", lowered)
        location = location_match.group(1).strip() if location_match else None
        return get_current_time(location)

    if re.search(r"\b(date|today|what day)\b", lowered):
        return get_current_date()

    if re.search(r"\b(news|headlines|latest)\b", lowered):
        topic_match = re.search(r"\b(?:about|on|for)\s+(.+)$", lowered)
        topic = topic_match.group(1).strip() if topic_match else None
        return get_latest_headlines(topic)

    return None
