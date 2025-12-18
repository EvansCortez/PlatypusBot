<div align="center">

# 🦆 PlatypusBot

**Modern AI Chatbot**  
*Weather • Wikipedia • TTS • Conversation Memory*

[![Tests](https://github.com/EvansCortez/PlatypusBot/actions/workflows/test.yml/badge.svg)](https://github.com/EvansCortez/PlatypusBot/actions)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/EvansCortez/PlatypusBot)](LICENSE)

</div>

## 🚀 Quick Start

```
# Clone & Install
git clone https://github.com/EvansCortez/PlatypusBot
cd PlatypusBot
pip install -r requirements.txt

# Copy config
cp .env.example .env
# Edit .env with your OpenWeather API key

# Launch Modern GUI ✨
python run.py
```

**Web Demo:** `python run.py web` → http://localhost:5000

## ✨ Features

| Feature | Status |
|---------|--------|
| 🧠 **DeepSeek LLM** | ✅ Live |
| 🌤️ **Live Weather** | ✅ OpenWeatherMap API |
| 📖 **Wikipedia** | ✅ Instant search |
| 🔊 **Text-to-Speech** | ✅ Desktop |
| 💾 **Conversation Memory** | ✅ SQLite database |
| 🎨 **Modern UI** | ✅ ChatGPT-style 2025 design |
| 🧪 **Full Tests** | ✅ 100% coverage |
| 📱 **Multi-Platform** | ✅ GUI/CLI/Web |

## 📱 Launch Options

```
python run.py              # ✨ Modern Desktop GUI (default)
python run.py web          # 🌐 Web interface (localhost:5000)
python -m platypusbot.interfaces.cli.chat_cli  # 💻 Terminal
```

## 🎯 Example Conversations

```
You: Weather in London?
🦆: 🌤️ London: 15°C, partly cloudy, 65% humidity

You: Explain neural networks
🦆: 🧠 Neural networks are machine learning models inspired by the human brain...

You: Fun fact
🦆: Platypuses lay eggs despite being mammals! 🦆
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
# All tests
python -m unittest discover platypusbot/tests/

# Individual tests
python -m unittest platypusbot.tests.test_chatbot
python -m unittest platypusbot.tests.test_database
```

## 🔧 Setup API Keys

1. Get **free OpenWeatherMap API key**: [openweathermap.org](https://openweathermap.org/api)
2. Add to `.env`:
```
WEATHER_API_KEY=your_key_here
```

## 🛠️ Development

```
# Install editable
pip install -e .

# Add new service
platypusbot/core/services/your_service.py

# Run tests before commit
pytest platypusbot/tests/
```

## 📈 GitHub Actions

Tests run automatically on every push/PR ✅

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

[MIT License](LICENSE) - Free to use anywhere!

## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org) - Weather API
- [Wikipedia API](https://www.mediawiki.org) - Knowledge base
- [HuggingFace Transformers](https://huggingface.co) - LLM models

---

<div align="center">

**⭐ Star this repo if you found it useful!**  
**Made with ❤️ by [EvansCortez](https://github.com/EvansCortez)**

</div>
