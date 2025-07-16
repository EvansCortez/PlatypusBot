from flask import Blueprint, request, jsonify, Response
from core.chatbot import Chatbot
from config import Config
import json

web_bp = Blueprint("web", __name__)
bot = Chatbot(Config)

@web_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message")
    conversation_id = data.get("conversation_id")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    result = bot.process_message(user_input, conversation_id)
    return jsonify(result)

@web_bp.route("/api/conversations", methods=["GET"])
def get_conversations():
    return jsonify(bot.db.get_conversations())

@web_bp.route("/api/conversations/<conv_id>/messages", methods=["GET"])
def get_messages(conv_id):
    return jsonify(bot.db.get_conversation_messages(conv_id))

@web_bp.route("/api/tts", methods=["POST"])
def tts():
    text = request.json.get("text")
    success = bot.services["tts"].speak(text)
    return jsonify({"success": success})
