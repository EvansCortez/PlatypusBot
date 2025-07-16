import requests

class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, location):
        if not self.api_key:
            return "Weather API key not configured."

        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        try:
            res = requests.get(self.BASE_URL, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()
            return (
                f"Weather in {data['name']}:\n"
                f"- {data['weather'][0]['description']}\n"
                f"- {data['main']['temp']}°C"
            )
        except Exception:
            return "Couldn't fetch weather data."
