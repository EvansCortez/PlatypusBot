# core/services/weather.py

import requests

class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return self.format_weather(data)
        except requests.RequestException:
            return "Sorry, I couldn't fetch the weather data."

    def format_weather(self, data):
        if not data or "main" not in data:
            return "Sorry, I couldn't fetch the weather data."
        return (
            f"Weather in {data['name']}:\n"
            f"- Temperature: {data['main']['temp']}°C\n"
            f"- Conditions: {data['weather'][0]['description']}\n"
            f"- Humidity: {data['main']['humidity']}%\n"
            f"- Wind: {data['wind']['speed']} m/s"
        )