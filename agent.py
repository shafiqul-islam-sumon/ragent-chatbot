import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import warnings
from config import Config
from dotenv import load_dotenv
from llm.gemini_llm import GeminiLLM
from tool_registry import ToolRegistry
from langchain_core.messages import SystemMessage
from langchain.agents import initialize_agent, AgentType
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage, BaseMessage
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()


class Agent:
    def __init__(self):
        prompt_content = self.load_prompt(Config.AGENT_PROMPT)
        system_prompt = SystemMessage(content=prompt_content)

        # Wrap Gemini LLM with system prompt using .with_config
        self.llm = GeminiLLM().get_client().with_config({
            "system_message": system_prompt
        })

        # Dynamically load all tools
        registry = ToolRegistry()
        tools = registry.get_all_tools()

        self.react_agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def load_prompt(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def run(self, query: str, history: list[BaseMessage] = None) -> str:
        # Copy full history
        messages = history.copy() if history else []

        # Append current user query
        messages.append(HumanMessage(content=query))

        try:
            return self.react_agent.invoke(messages)
        except OutputParserException as e:
            print("⚠️ OutputParserException:", e)

        # Fallback: use the LLM directly to answer
        return self.llm.invoke(messages)


if __name__ == "__main__":
    agent = Agent()
    user_query = "What is the full form of K12HSN?"
    answer = agent.run(user_query)
    print("\n### Agent Response:\n", answer)
