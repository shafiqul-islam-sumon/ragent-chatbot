import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import json
import hashlib
import pandas as pd
from config import Config
from utils.nltk import NLTK
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from utils.normalizer import Normalizer
from qdrant_client.models import ScoredPoint
from langchain_core.documents import Document
from vector_db.chunker import DocumentChunker
from vector_db.data_embedder import BAAIEmbedder
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchText
from qdrant_client.models import TextIndexParams, TextIndexType, TokenizerType
from langchain_community.document_loaders import (
    PDFPlumberLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
    TextLoader,
    CSVLoader,
    JSONLoader
)

load_dotenv()


class QdrantDBClient:
    def __init__(self):
        self.collection_name = Config.COLLECTION_NAME
        self.client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))  # Qdrant - Cloud
        #self.client = QdrantClient(path=Config.QDRANT_PERSIST_PATH)  # Qdrant - Local
        self.embedder = BAAIEmbedder()
        self.chunker = DocumentChunker()
        self.normalizer = Normalizer()
        self.nltk = NLTK()

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.model.get_sentence_embedding_dimension(),
                    distance=Distance.COSINE,
                )
            )

        # Optional performance optimization
        self.client.update_collection(
            collection_name=self.collection_name,
            optimizers_config={"default_segment_number": 2}
        )

        # Add BM25 support on 'tokenized_text' field
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="tokenized_text",
            field_schema=TextIndexParams(
                type=TextIndexType.TEXT,
                tokenizer=TokenizerType.WHITESPACE,
                min_token_len=1,
                max_token_len=20,
                lowercase=False
            )
        )

    def tokenize_for_bm25(self, text: str) -> str:
        norm_text = self.normalizer.normalize_text(text)
        tokens = norm_text.split()
        filtered_tokens = [t for t in tokens if t.lower() not in self.nltk.stopwords]
        return " ".join(filtered_tokens)

    def get_jq_schema(self, file_path: str) -> str:
        """
        Dynamically determines the jq_schema based on whether the JSON root is a list or a dict.
        Handles:
          - Root list: [. {...}, {...}]
          - Root dict with list key: { "key": [ {...}, {...} ] }

        Raises:
            ValueError: If no valid list is found.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return ".[]"

        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    return f".{key}[]"

            raise ValueError("No list found in the top-level JSON object.")

        else:
            raise ValueError("Unsupported JSON structure: must be list or dict")

    def load_excel_with_headers(self, file_path):
        df = pd.read_excel(file_path)
        docs = []

        for i, row in df.iterrows():
            text = "\n".join([f"{col}: {row[col]}" for col in df.columns])
            metadata = {"source": file_path, "row_index": i}
            docs.append(Document(page_content=text, metadata=metadata))

        return docs

    def load_and_chunk_docs(self, file_path: str) -> List[dict]:
        ext = os.path.splitext(file_path)[1]
        if ext == ".pdf":
            docs = PDFPlumberLoader(file_path).load()
        elif ext == ".docx":
            docs = UnstructuredWordDocumentLoader(file_path).load()
        elif ext == ".xlsx":
            #docs = UnstructuredExcelLoader(file_path).load()
            docs = self.load_excel_with_headers(file_path)
        elif ext == ".pptx":
            docs = UnstructuredPowerPointLoader(file_path).load()
        elif ext == ".txt":
            docs = TextLoader(file_path, encoding="utf-8").load()
        elif ext == ".csv":
            docs = CSVLoader(file_path).load()
        elif ext == ".json":
            docs = JSONLoader(file_path, jq_schema=self.get_jq_schema(file_path), text_content=False).load()
        else:
            return []

        # Add source metadata to each Document
        for doc in docs:
            doc.metadata["source"] = os.path.basename(file_path)

        return self.chunker.split_documents(docs)

    def hash_text(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def insert_chunks(self, chunk_dicts: List[dict]):
        seen_hashes = set()
        all_points = []

        texts = [self.normalizer.normalize_text(d["text"]) for d in chunk_dicts]
        embeddings = self.embedder.embed_documents(texts)

        for i, chunk in enumerate(chunk_dicts):
            text = self.normalizer.normalize_text(chunk["text"])

            chunk_hash = self.hash_text(text)
            if chunk_hash in seen_hashes:
                continue
            seen_hashes.add(chunk_hash)

            tokenized_text = self.tokenize_for_bm25(text)

            all_points.append(
                PointStruct(
                    id=chunk["id"],
                    vector=embeddings[i],
                    payload={
                        "text": text,
                        "tokenized_text": tokenized_text,
                        **chunk["metadata"]
                    }
                )
            )

        for i in range(0, len(all_points), Config.BATCH_SIZE):
            self.client.upsert(collection_name=self.collection_name, points=all_points[i:i + Config.BATCH_SIZE])

    def search(self, query: str, top_k: int = Config.TOP_K) -> List[Document]:
        query = self.normalizer.normalize_text(query)
        query_embedding = self.embedder.embed_query(query)
        query_tokens = self.tokenize_for_bm25(query).split()

        # print(f"\n🔍 Query: {query}")
        # print(f"🔑 Query Tokens: {query_tokens}")

        # BM25 Search
        bm25_results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                should=[
                    FieldCondition(
                        key="tokenized_text",
                        match=MatchText(text=token)
                    ) for token in query_tokens
                ]
            ),
            limit=top_k
        )[0]

        bm25_dict = {
            pt.payload.get("text", ""): {
                "source": "BM25",
                "bm25_score": getattr(pt, "score", 0.0),  # Handle missing scores
                "vector_score": 0.0,
                "metadata": pt.payload or {}
            }
            for pt in bm25_results
        }

        # print(f"\n### BM25 Results ({len(bm25_dict)}):")
        # for i, (text, info) in enumerate(bm25_dict.items(), 1):
        #     print(f"{i}. {text[:100]}... | BM25 Score: {info['bm25_score']:.4f}")

        # Vector Search (using query_points instead of deprecated search)
        vector_results: List[ScoredPoint] = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        ).points

        vector_dict = {
            pt.payload.get("text", ""): {
                "source": "Vector",
                "bm25_score": 0.0,
                "vector_score": getattr(pt, "score", 0.0),  # Handle missing scores
                "metadata": pt.payload or {}
            }
            for pt in vector_results
        }

        # print(f"\n### Vector Results ({len(vector_dict)}):")
        # for i, (text, info) in enumerate(vector_dict.items(), 1):
        #     print(f"{i}. {text[:100]}... | Vector Score: {info['vector_score']:.4f}")

        # Merge & Deduplicate Results
        combined_results: Dict[str, Dict] = {}

        for text, info in bm25_dict.items():
            combined_results[text] = {
                "source": info["source"],
                "bm25_score": info["bm25_score"],
                "vector_score": 0.0,
                "metadata": info["metadata"]
            }

        for text, info in vector_dict.items():
            if text in combined_results:
                combined_results[text]["source"] = "Hybrid"
                combined_results[text]["vector_score"] = info["vector_score"]
            else:
                combined_results[text] = {
                    "source": info["source"],
                    "bm25_score": 0.0,
                    "vector_score": info["vector_score"],
                    "metadata": info["metadata"]
                }

        # Compute Hybrid Score
        for text in combined_results:
            combined_results[text]["final_score"] = (
                    Config.ALPHA * combined_results[text]["bm25_score"]
                    + (1 - Config.ALPHA) * combined_results[text]["vector_score"]
            )

        # Sort and return as LangChain Documents
        sorted_results = sorted(combined_results.items(), key=lambda x: x[1]["final_score"], reverse=True)

        # print(f"\n### Combined Results (Sorted by Final Score):")
        # for i, (text, info) in enumerate(sorted_results, 1):
        #     print(f"{i}. {text[:100]}... | Final Score: {info['final_score']:.4f} | "
        #           f"BM25: {info['bm25_score']:.4f} | Vector: {info['vector_score']:.4f} | Source: {info['source']}")

        return [
            Document(
                page_content=text,
                metadata={
                    **info["metadata"],
                    "source": info["source"],
                    "bm25_score": info["bm25_score"],
                    "vector_score": info["vector_score"],
                    "final_score": info["final_score"]
                }
            )
            for text, info in sorted_results  # Don't Remove zero-score docs
            #for text, info in sorted_results if info["final_score"] > 0  # Remove zero-score docs
        ]

    def export_all_documents(self, output_dir: str = Config.STORED_CHUNK_DIR):
        """Export all inserted documents from Qdrant grouped by source."""
        os.makedirs(output_dir, exist_ok=True)

        file_text_map = {}
        next_offset = None

        while True:
            points, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                with_payload=True,
                with_vectors=False,
                limit=1000,  # You can tune this batch size
                offset=next_offset
            )

            for pt in points:
                payload = pt.payload or {}
                source = payload.get("source", "unknown_file.txt")
                text = payload.get("text", "")
                if not text.strip():
                    continue
                file_text_map.setdefault(source, []).append((text, payload.get("chunk_order", 0)))

            if next_offset is None:
                break

        # Write all collected texts grouped by file name
        for source, chunks in file_text_map.items():
            file_name = os.path.splitext(os.path.basename(source))[0]
            file_path = os.path.join(output_dir, f"{file_name}.txt")

            # Sort by chunk_order
            sorted_chunks = sorted(chunks, key=lambda x: x[1])

            with open(file_path, "w", encoding="utf-8") as f:
                for chunk_text, chunk_order in sorted_chunks:
                    f.write(f"### Chunk Order: {chunk_order}\n")
                    f.write(chunk_text.strip() + "\n\n---\n\n")

        print(f"### Exported {len(file_text_map)} source files to '{output_dir}'")

    def clear_qdrant_db(self):
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(collection_name=self.collection_name) # deletes full collection
            print("### All data is removed")


if __name__ == "__main__":
    qdrant_db_client = QdrantDBClient()
    data_dir = Config.DATA_DIR

    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        ext = os.path.splitext(filename)[1].lower()

        if os.path.isfile(file_path) and ext in Config.FILE_EXTENSIONS:
            print(f"📄 Processing: {filename}")
            chunk_dicts = qdrant_db_client.load_and_chunk_docs(file_path)
            qdrant_db_client.insert_chunks(chunk_dicts)

    print(f"### Total documents in collection: {qdrant_db_client.client.count(qdrant_db_client.collection_name)}")

    qdrant_db_client.export_all_documents()
    #qdrant_db_client.clear_qdrant_db()

    query = "What is the full form of K12HSN?"
    docs = qdrant_db_client.search(query)
    print(f"\n### Retrieved {len(docs)} results:")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. {doc.page_content[:]}...")

