import wikipediaapi
from datetime import datetime
from tools.base_tool import BaseTool


class WikipediaTool(BaseTool):
    """A tool for fetching Wikipedia summaries."""

    def __init__(self):
        super().__init__(
            name="wikipedia",
            description=(
                "Use this tool to get general knowledge or definitions about well-known people, places, or concepts from Wikipedia. "
                "Works best when the query is a specific topic or name like 'Albert Einstein' or 'blockchain'. "
                "Use this if the question is not document-related and RAG is not helpful."
            )

        )
        self.wiki_api = wikipediaapi.Wikipedia(user_agent="chatbot_user")

    def run(self, query: str) -> str:
        """Fetches summary information from Wikipedia for a given topic."""
        if not query or not query.strip():
            return "Error: Query cannot be empty."

        try:
            page = self.wiki_api.page(query)

            if page.exists():
                today = datetime.now().strftime("%Y-%m-%d")
                return f"(Today is {today}) {page.summary.strip()}"

            return f"Error: No Wikipedia page found for '{query}'."

        except Exception as e:
            return f"Error: An error occurred while searching Wikipedia: {str(e)}"


# === For standalone testing ===
if __name__ == "__main__":

    wikipedia_tool = WikipediaTool()
    queries = ["Julian Alvarez"]

    for query in queries:
        result = wikipedia_tool.run(query)
        if result:
            print(f"Result for '{query}':\n{result}\n")
        else:
            print(f"No result found for '{query}'\n")
