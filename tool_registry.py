import pkgutil
import importlib
from typing import Dict, List
from langchain.tools import Tool
from tools.base_tool import BaseTool


class ToolRegistry:
    """Registry for dynamically loading and managing tools."""

    def __init__(self, tools_package: str = "tools"):
        self.tools_package = tools_package
        self.tools: Dict[str, BaseTool] = {}
        self.register_tools()

    def register_tools(self):
        """Dynamically registers all available tools in the tools package."""
        tool_modules = [name for _, name, _ in pkgutil.iter_modules([self.tools_package])]

        for module_name in tool_modules:
            try:
                module = importlib.import_module(f"{self.tools_package}.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseTool)
                        and attr is not BaseTool
                    ):
                        tool_instance = attr()
                        self.tools[tool_instance.name.lower()] = tool_instance
            except Exception as e:
                print(f"[ERROR] Failed to register tool '{module_name}': {e}")

    def get_tool(self, name: str) -> BaseTool:
        """Retrieve a tool by name."""
        return self.tools.get(name.lower())

    def list_tools(self) -> str:
        """Returns a formatted string listing available tools."""
        return "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools.values()]
        )

    def all(self) -> Dict[str, BaseTool]:
        """Returns all registered tools as a dictionary."""
        return self.tools

    def get_all_tools(self) -> List[Tool]:
        """Returns tools as LangChain Tool objects."""
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                func=tool.run
            )
            for tool in self.all().values()
        ]


if __name__=="__main__":
    registry = ToolRegistry()

    print("🔧 Registered Tools:\n")
    print(registry.list_tools())

    # Example usage
    tools = registry.get_all_tools()
    print("\n### LangChain Tool Definitions:")
    for t in tools:
        print(t["name"], "-", t["description"])

    # query = "what is the capital of Japan?"
    # tool = registry.get_tool("web_search")
    #
    # if tool:
    #     result = tool.run(query)
    #     print("\n### Web Search Result:")
    #     for item in result:
    #         print(item)
    # else:
    #     print("Tool not found.")
