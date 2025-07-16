import spacy

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process_input(self, text, context=None):
        doc = self.nlp(text.lower())
        entities = {ent.text: ent.label_ for ent in doc.ents}

        intent = "general"
        if any(tok.text in ["weather"] for tok in doc):
            intent = "weather"
        elif any(tok.text in ["wikipedia", "wiki"] for tok in doc):
            intent = "wikipedia"
        elif any(tok.text in ["explain"] for tok in doc):
            intent = "explanation"

        return {
            "text": text,
            "intent": intent,
            "entities": entities,
            "context": context or []
        }
