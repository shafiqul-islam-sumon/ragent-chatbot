import hashlib
from typing import List
from config import Config
from utils.normalizer import Normalizer
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentChunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.existing_hashes = set()
        self.normalizer = Normalizer()

    def hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def split_documents(self, docs: List[Document]) -> List[dict]:
        """Split and deduplicate documents. Returns list of dicts with id, text, metadata."""
        chunks = self.splitter.split_documents(docs)
        results = []

        for i, chunk in enumerate(chunks):
            normalized_text = self.normalizer.normalize_text(chunk.page_content)
            if not normalized_text:
                continue
            chunk_hash = self.hash_text(normalized_text)
            if chunk_hash in self.existing_hashes:
                continue
            self.existing_hashes.add(chunk_hash)

            results.append({
                "id": int(chunk_hash, 16) % (10 ** 9),
                "text": normalized_text,
                "metadata": {
                    **chunk.metadata,
                    "chunk_order": i  # Preserve order
                }
            })

        return results


if __name__ == "__main__":

    sample_docs = [
        Document(
            page_content="This is a long document that needs to be split into smaller pieces.",
            metadata={"source": "example.txt"}
        )
    ]

    chunker = DocumentChunker()
    chunks = chunker.split_documents(sample_docs)

    for i, cnk in enumerate(chunks):
        print(f"#### Chunk {i}: {cnk['text']}")

