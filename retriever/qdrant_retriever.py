from config import Config
from typing import List, Optional
from langchain_core.documents import Document
from vector_db.qdrant_db import QdrantDBClient
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables.config import RunnableConfig


class QdrantRetriever(BaseRetriever):
    def __init__(self):
        super().__init__()
        self._qdrant_client = QdrantDBClient()
        self._k = Config.TOP_K

    def _get_relevant_documents(self, input: str, *, config: Optional[RunnableConfig] = None) -> List[Document]:
        docs = self._qdrant_client.search(query=input, top_k=self._k)
        return docs


if __name__ == "__main__":
    retriever = QdrantRetriever()
    query = "Who is the president of the United States?"

    docs = retriever.invoke(query)
    print(f"\n### Top {len(docs)} documents:")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. {doc.page_content[:200]}...")
