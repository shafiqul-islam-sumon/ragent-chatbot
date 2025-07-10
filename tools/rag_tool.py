from rag import RAGPipeline
from tools.base_tool import BaseTool


class RAGTool(BaseTool):
    """A tool for answering queries using a vector store-backed RAG pipeline."""

    def __init__(self):
        super().__init__(
            name="rag_search",
            description=(
                "Use this tool to answer factual, abbreviation-based, educational, or document-related questions. "
                "It searches internal documents using a vector database. "
                "Always try this first before considering external tools like web_search, wikipedia, weather etc."
            )
        )
        self.rag = RAGPipeline()

    def run(self, query: str) -> str:
        """Run the RAG pipeline for the given query and return the answer."""
        if not query or not query.strip():
            return "❌ Query cannot be empty."
        try:
            return self.rag.ask(query)
        except Exception as e:
            return f"⚠️ RAG processing failed: {str(e)}"


# === For standalone testing ===
if __name__ == "__main__":
    rag_tool = RAGTool()
    question = "What is K12HSN?"
    answer = rag_tool.run(question)
    print(f"Q: {question}\nA: {answer}")
