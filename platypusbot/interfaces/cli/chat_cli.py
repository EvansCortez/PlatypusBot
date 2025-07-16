import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.chatbot import Chatbot
from config import Config

def main():
    bot = Chatbot(Config)
    print("Welcome to PlatypusBot CLI!")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("> ")
        if user_input.strip().lower() == "exit":
            print("Goodbye!")
            break

        result = bot.process_message(user_input)
        print("Bot:", result.get("response", "Sorry, I have no response."))

if __name__ == "__main__":
    main()
