import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.chatbot import Chatbot
from config import Config

import pytest

@pytest.fixture
def bot():
    return Chatbot(Config)

def test_greeting(bot):
    result = bot.process_message("hello")
    assert "response" in result
    assert any(greet in result["response"].lower() for greet in ["hi", "hello", "hey"])

def test_general_response(bot):
    result = bot.process_message("Tell me a fun fact")
    assert "response" in result
