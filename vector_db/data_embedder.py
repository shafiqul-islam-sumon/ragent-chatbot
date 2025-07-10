import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from typing import List
from config import Config
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer


class BAAIEmbedder(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
        self.batch_size = Config.BATCH_SIZE

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, batch_size=self.batch_size, show_progress_bar=True, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()


if __name__ == "__main__":
    embedder = BAAIEmbedder()
    sample_texts = ["LangChain is powerful", "Qdrant is great for vectors"]
    embeddings = embedder.embed_documents(sample_texts)
    print("### Sample embeddings (first 5 dims):")
    for emb in embeddings:
        print(emb[:5])
