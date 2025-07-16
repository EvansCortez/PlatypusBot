import wikipedia

class WikipediaService:
    def search(self, query):
        try:
            return wikipedia.summary(query, sentences=2)
        except wikipedia.exceptions.DisambiguationError as e:
            return "Multiple results: " + ", ".join(e.options[:3])
        except wikipedia.exceptions.PageError:
            return "No page found."
        except Exception:
            return "Error searching Wikipedia."
