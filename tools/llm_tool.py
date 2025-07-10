import os
from config import Config
from tools.base_tool import BaseTool
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMInstructionTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="llm_instruction",
            description=(
                "Handles creative and instructional tasks using an LLM. "
                "Use this tool for tasks like summarizing, rewriting, poem generation, storytelling, or following general instructions "
                "when no specific tool is applicable."
            )
        )
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=os.environ["GOOGLE_API_KEY"],
            model=Config.LLM_MODEL,
            temperature=Config.TEMPERATURE
        )

    def run(self, input_data: str) -> str:
        if not input_data.strip():
            return "Error: Empty input for LLM tool."

        try:
            response = self.llm.invoke([HumanMessage(content=input_data)])
            return response.content.strip()
        except Exception as e:
            return f"Failed to run LLM tool: {str(e)}"


# === For standalone testing ===
if __name__ == "__main__":
    tool = LLMInstructionTool()
    test_input = "Rewrite this in a more formal tone.. Hey there! Just wanted to say thanks for your help yesterday. It really meant a lot."
    result = tool.run(test_input)
    print(result)
