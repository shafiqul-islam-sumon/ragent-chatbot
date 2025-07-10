import os
import nltk
from config import Config
from nltk.corpus import stopwords
from nltk.data import path as nltk_path


class NLTK:
    def __init__(self):
        # Define your custom download path (e.g., current directory)
        self.nltk_data_path = Config.NLTK_DIR

        # Tell NLTK to look in your custom location
        nltk_path.append(self.nltk_data_path)

        self.download_stopwords()

        self.stopwords = set(stopwords.words('english'))
        self.punctuation = {".", ",", ";", ":", "'", '"', "~", "-", "–", "—", "(", ")", "[", "]", "{", "}", "!", "?", "`"}

    def download_stopwords(self):
        # Full path to the English stopwords file
        stopwords_path = os.path.join(self.nltk_data_path, "corpora", "stopwords", "english")

        if not os.path.exists(stopwords_path):
            nltk.download("stopwords", download_dir=self.nltk_data_path)
