<div align="center">

# PlatypusBot

Purpose-built chatbot package with a shared core, desktop GUI, browser chatbox, terminal UI, live-data services, optional OpenAI responses, multilingual routing, and SQLite conversation memory.

</div>

## 🚀 Quick Start

```
pip install -r requirements.txt

cp .env.example .env
# Add your OpenWeather API key if you want live weather

# Launch the desktop app
python run.py
```

## ✨ Features

| Feature | Status |
|---------|--------|
| 🌤️ **Live Weather** | ✅ OpenWeatherMap API |
| 📰 **Realtime Headlines/Time** | ✅ Service routing |
| 📖 **Wikipedia** | ✅ Instant search |
| 🧠 **Optional LLM Layer** | ✅ OpenAI Responses API |
| 🌍 **Multilingual Prompts** | ✅ Routed with translation support |
| 🔊 **Text-to-Speech** | ✅ Optional desktop support |
| 💾 **Conversation Memory** | ✅ SQLite database |
| 🎨 **Desktop GUI** | ✅ Tkinter app |
| 🌐 **Web Chatbox** | ✅ Modern browser interface |
| 💻 **CLI** | ✅ Terminal app |
| 🧪 **Tests** | ✅ Included |

## 📱 Launch Options

```
python run.py              # Desktop GUI (default)
python run.py gui          # Desktop GUI
python run.py web          # Browser chatbox on localhost:5000
python run.py cli          # Terminal interface
python -m platypusbot.interfaces.cli.chat_cli  # 💻 Terminal
```

## 🎯 Example Conversations

```
You: Weather in London?
PlatypusBot: Weather in London: 15°C, partly cloudy, 65% humidity.

You: Explain neural networks in French
PlatypusBot: [LLM-backed or translated response when configured]

You: Fun fact
PlatypusBot: Platypuses are mammals that lay eggs.
```

## 📁 Project Structure

```
PlatypusBot/
├── platypusbot/                    # Main package
│   ├── core/                      # 🤖 AI Brain
│   │   ├── chatbot.py            # Main logic
│   │   ├── services/             # Weather/Wiki/TTS
│   │   └── database.py           # Conversation history
│   ├── interfaces/               # 🎨 All UIs
│   │   ├── gui/                  # Modern desktop
│   │   └── cli/                  # Terminal
│   └── tests/                    # 🧪 Test suite
├── run.py                        # 🚀 Launcher
├── requirements.txt
└── .env.example
```

## 🧪 Run Tests

```
python -m unittest discover platypusbot/tests/
```

## 🔧 Setup API Keys

1. Get **free OpenWeatherMap API key**: [openweathermap.org](https://openweathermap.org/api)
2. Add to `.env`:
```
WEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-mini
LIBRETRANSLATE_URL=https://your-libretranslate-instance
```

## 📄 License

[MIT License](LICENSE) - Free to use anywhere!
