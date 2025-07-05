# core/nlp_processor.py
from typing import Dict
import spacy

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.context = {}

    def process_input(self, text: str) -> Dict:
        doc = self.nlp(text)
        entities = {ent.text: ent.label_ for ent in doc.ents}
        # Placeholder for intent recognition
        intent = "default"
        confidence = 1.0
        return {
            "text": text,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "context": self.context
        }

    def update_context(self, key: str, value: str):
        self.context[key] = value