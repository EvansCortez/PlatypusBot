from __future__ import annotations

import os

import requests


def get_weather(city: str) -> str:
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "Weather is configured, but WEATHER_API_KEY is missing from your environment."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return "I couldn't connect to the weather service right now."

    payload = response.json()
    main = payload.get("main", {})
    weather = payload.get("weather", [{}])[0]
    temp = main.get("temp")
    humidity = main.get("humidity")
    description = weather.get("description", "unavailable conditions")
    if temp is None or humidity is None:
        return f"I found weather data for {city}, but it was incomplete."
    return f"Weather in {city.title()}: {temp}°C, {description}, {humidity}% humidity."
