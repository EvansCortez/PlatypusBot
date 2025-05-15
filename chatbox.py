import os
import ssl
import random
import sqlite3
import wikipedia
import requests
import pyttsx3
import speech_recognition as sr
import sympy
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk
from nltk.sentiment import SentimentIntensityAnalyzer
from urllib.request import getproxies
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

class Chatbot:
    def __init__(self):
        self.setup_nltk()
        self.setup_dependencies()
        self.initialize_data()
        
    def setup_nltk(self):
        """Initialize NLTK with required downloads"""
        try:
            import nltk
            # Handle SSL certificate issues
            if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(ssl, "_create_unverified_context", None):
                ssl._create_default_https_context = ssl._create_unverified_context

            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
        except Exception as e:
            print(f"Error setting up NLTK: {e}")
            exit()

    def setup_dependencies(self):
        """Check for required dependencies"""
        required_modules = {
            'wikipedia': 'pip install wikipedia',
            'requests': 'pip install requests',
            'pyttsx3': 'pip install pyttsx3',
            'speech_recognition': 'pip install SpeechRecognition',
            'sympy': 'pip install sympy',
            'sklearn': 'pip install scikit-learn'
        }
        
        for module, install_cmd in required_modules.items():
            try:
                __import__(module)
            except ImportError:
                print(f"The '{module}' module is not installed. Please install it using '{install_cmd}'")
                exit()

    def initialize_data(self):
        """Initialize all data structures"""
        self.GREETING_INPUTS = ("hello", "hi", "greetings", "hey", "how are you?", "what's up?", "yo")
        self.GREETING_RESPONSES = ["Hi there!", "Hello!", "Hey!", "Greetings!", "Great!", "What's good?", "Yo!"]
        
        self.FUN_FACTS = [
            "The world's longest concert lasted 453 hours.",
            "Africa is the only continent in all four hemispheres.",
            "Japan has one vending machine for every 40 people."
        ]
        
        self.SCIENCE_FACTS = [
            "Water boils at 100 degrees Celsius at sea level.",
            "The Earth revolves around the Sun in approximately 365.25 days.",
            "The human brain contains around 86 billion neurons."
        ]
        
        self.CS_CONCEPTS = {
            "algorithm": "An algorithm is a step-by-step procedure for solving a problem.",
            "data structure": "A way of organizing and storing data efficiently.",
            "machine learning": "AI field using algorithms to learn from data."
        }
        
        # Initialize speech engine once
        self.speech_engine = pyttsx3.init()
        
        # Setup database connection
        self.db_conn = sqlite3.connect("chat_history.db", check_same_thread=False)
        self.setup_database()

    def setup_database(self):
        """Initialize the database table"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT,
                    response TEXT
                )
            """)
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def save_chat_history(self, user_input, response):
        """Save conversation to database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT INTO history (user_input, response) VALUES (?, ?)",
                (user_input, response)
            )
            self.db_conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving chat history: {e}")

    def greet(self, sentence):
        """Handle greeting responses"""
        for word in sentence.split():
            if word.lower() in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES)
        return None

    def solve_math(self, expression):
        """Solve mathematical expressions"""
        try:
            result = sympy.sympify(expression)
            return f"The result of {expression} is {result}."
        except Exception as e:
            return "I couldn't solve that math problem. Please check your input."

    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            wikipedia.set_lang("en")
            result = wikipedia.summary(query, sentences=2)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Try being more specific. Options: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return "No Wikipedia page found for this query."
        except Exception as e:
            return f"An error occurred while searching Wikipedia: {str(e)}"

    def get_weather(self, city):
        """Get weather information for a city"""
        api_key = "your_api_key"  # Replace with your API key
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return (
                    f"The weather in {city} is {data['weather'][0]['description']} "
                    f"with a temperature of {data['main']['temp']}°C."
                )
            return "I couldn't fetch the weather. Please check the city name."
        except requests.exceptions.RequestException:
            return "I couldn't connect to the weather service. Please try again later."

    def analyze_sentiment(self, text):
        """Analyze text sentiment"""
        try:
            sia = SentimentIntensityAnalyzer()
            sentiment = sia.polarity_scores(text)
            if sentiment['compound'] >= 0.05:
                return "The sentiment is Positive 😊"
            elif sentiment['compound'] <= -0.05:
                return "The sentiment is Negative 😞"
            else:
                return "The sentiment is Neutral 😐"
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

    def speak(self, text):
        """Convert text to speech"""
        try:
            self.speech_engine.say(text)
            self.speech_engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def listen(self):
        """Listen to user voice input"""
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "Sorry, I'm having trouble with the speech service."
        except Exception as e:
            return f"Error in speech recognition: {str(e)}"

    def generate_response(self, user_input):
        """Generate appropriate response based on user input"""
        # First check for greetings
        greeting = self.greet(user_input)
        if greeting:
            return greeting

        # Process commands
        if not user_input.strip():
            return "I didn't hear anything. Could you repeat that?"

        user_input = user_input.lower()
        
        if "classify" in user_input:
            training_data = ["I love this!", "This is terrible.", "Amazing!", "Worst ever."]
            labels = ["positive", "negative", "positive", "negative"]
            text_to_classify = user_input.replace("classify", "").strip()
            if text_to_classify:
                try:
                    classification = self.classify_text(text_to_classify, training_data, labels)
                    return f"I classify this as: {classification}"
                except Exception as e:
                    return f"Error in classification: {str(e)}"
            return "Please provide some text to classify after 'classify'"

        elif "weather" in user_input:
            city = user_input.replace("weather", "").replace("in", "").strip()
            if city:
                return self.get_weather(city)
            return "Please specify a city for weather information"

        elif "sentiment" in user_input:
            text = user_input.replace("sentiment", "").strip()
            if text:
                return self.analyze_sentiment(text)
            return "Please provide some text to analyze after 'sentiment'"

        elif "wikipedia" in user_input:
            query = user_input.replace("wikipedia", "").strip()
            if query:
                return self.search_wikipedia(query)
            return "What would you like me to search on Wikipedia?"

        elif "solve" in user_input:
            expression = user_input.replace("solve", "").strip()
            if expression:
                return self.solve_math(expression)
            return "Please provide a math problem to solve"

        elif "fun fact" in user_input or "tell me something" in user_input:
            return random.choice(self.FUN_FACTS)

        elif "science fact" in user_input:
            return random.choice(self.SCIENCE_FACTS)

        elif "explain" in user_input:
            concept = user_input.replace("explain", "").strip()
            if concept in self.CS_CONCEPTS:
                return self.CS_CONCEPTS[concept]
            return "I don't have information on that concept. Try: " + ", ".join(self.CS_CONCEPTS.keys())

        elif "name" in user_input:
            return "I'm your helpful chatbot assistant!"

        elif "help" in user_input:
            return (
                "I can help with: \n"
                "- Greetings and chat\n"
                "- Weather information (say 'weather in [city]')\n"
                "- Wikipedia searches (say 'wikipedia [topic]')\n"
                "- Math problems (say 'solve [expression]')\n"
                "- Fun facts and science facts\n"
                "- Explaining CS concepts\n"
                "- Sentiment analysis (say 'sentiment [text]')"
            )

        return "I'm not sure how to respond to that. Try asking for 'help' to see what I can do."

    def classify_text(self, text, training_data, labels):
        """Classify text using Naive Bayes"""
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(training_data)
        model = MultinomialNB()
        model.fit(X, labels)
        return model.predict(vectorizer.transform([text]))[0]

    def run(self):
        """Main chat loop"""
        print("Chatbot: Hello! Type 'exit' to end the conversation or say 'help' for options.")
        
        while True:
            try:
                # Get user input (text or voice)
                input_method = input("Choose input method (1 for text, 2 for voice): ").strip()
                
                if input_method == '1':
                    user_input = input("You: ")
                elif input_method == '2':
                    print("Please speak now...")
                    user_input = self.listen()
                    print(f"You said: {user_input}")
                else:
                    print("Invalid option. Using text input.")
                    user_input = input("You: ")
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    print("Chatbot: Goodbye!")
                    self.db_conn.close()
                    break
                
                response = self.generate_response(user_input)
                print("Chatbot:", response)
                self.speak(response)
                self.save_chat_history(user_input, response)
                
            except KeyboardInterrupt:
                print("\nChatbot: Goodbye!")
                self.db_conn.close()
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue

if __name__ == "__main__":
    chatbot = Chatbot()
    chatbot.run()