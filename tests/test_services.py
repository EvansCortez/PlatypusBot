import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.services.wikipedia import WikipediaService
from core.services.weather import WeatherService

def test_wikipedia_search():
    service = WikipediaService()
    result = service.search("Python (programming language)")
    assert "Python" in result

def test_weather_service():
    service = WeatherService(api_key=None)
    result = service.get_weather("London")
    assert "Weather API key not configured." in result
