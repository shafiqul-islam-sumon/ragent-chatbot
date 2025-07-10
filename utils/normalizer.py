import unicodedata


class Normalizer:
    def __init__(self):
        pass

    def normalize_text(self, text: str) -> str:
        # Unicode normalization (e.g., full-width → half-width, etc.)
        text = unicodedata.normalize("NFKC", text)

        # Lowercase
        #text = text.lower()

        # Remove punctuation
        #text = "".join(char for char in text if char not in self.punctuation)

        # Collapse multiple whitespace
        #text = re.sub(r"\s+", " ", text).strip()

        return text

