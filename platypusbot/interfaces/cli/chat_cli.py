from __future__ import annotations

from platypusbot.core.chatbot import Chatbot


def run_cli() -> None:
    bot = Chatbot()
    bot.set_preference("interface", "cli")
    print("PlatypusBot: Hello! Type 'exit' to end the conversation or 'help' for options.")
    try:
        while True:
            input_method = input("Choose input method (1 for text, 2 for voice): ").strip() or "1"
            if input_method == "2":
                print("Listening...")
                user_input = bot.listen()
                if user_input:
                    print(f"You said: {user_input}")
            else:
                user_input = input("You: ")

            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("PlatypusBot: Goodbye!")
                break

            response = bot.handle_message(user_input)
            print(f"PlatypusBot: {response}")
            bot.speak(response)
    finally:
        bot.close()


if __name__ == "__main__":
    run_cli()
