# You need to install python-dotenv to use load_dotenv.
# Run this in your terminal:
# pip install python-dotenv

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_PATH = os.getenv("DB_PATH", "chat_data.db")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/deepseek-llm-7b")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
