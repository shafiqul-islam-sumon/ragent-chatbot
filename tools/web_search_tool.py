import os
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from tools.base_tool import BaseTool

load_dotenv()


class WebSearchTool(BaseTool):
    """A tool for performing web searches using the Tavily API."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description=(
                "Use this tool to find up-to-date or real-time information from the web. "
                "Best for current events, recent news, trending topics, or anything not covered in internal documents or Wikipedia. "
                "Input should be a full natural-language query, e.g., 'Champion of the 2024 Champions League'."
            )
        )

        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Missing API Key: Please set 'TAVILY_API_KEY' in the .env file.")

        self.tavily_client = TavilyClient(api_key=self.api_key)

    def run(self, query: str) -> str:
        """Performs a web search for a given query and returns summarized results as a string."""
        if not query or not query.strip():
            return "Error: Query cannot be empty."

        # Append today's date to guide LLM reasoning
        today = datetime.now().strftime("%Y-%m-%d")
        query_with_date = f"(Today is {today}) {query}"

        try:
            search_results = self.tavily_client.search(query=query_with_date, max_results=2)

            if not search_results or "results" not in search_results:
                return "Error: No search results available."

            results = search_results["results"]
            if not results:
                return "Error: No results found."

            # Format the top results as a readable string
            formatted = []
            for i, result in enumerate(results, start=1):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "No URL")
                formatted.append(f"{i}. **{title}**\n{content}\n🔗 {url}")

            return "\n\n".join(formatted)

        except Exception as e:
            return f"Error: Search request failed: {str(e)}"


# === For standalone testing ===
if __name__ == "__main__":

    queries = ["F1 winner 2024"]
    web_search_tool = WebSearchTool()

    for query in queries:
        results = web_search_tool.run(query)
        if results:
            print(f"Context for '{query}':")
            for res in results:
                print(res)
            print("\n")
        else:
            print(f"No context found for '{query}'\n")