import math
import numexpr
from tools.base_tool import BaseTool


class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description=(
                "Evaluates structured math expressions. Use this tool to solve arithmetic problems. "
                "Before calling, convert natural language to proper Python-style math expressions. "
                "Examples: '2+2', '37593 * 67', '2**5', 'pi * 2**2', '37593**(1/5)'. "
                "Supports constants like pi and e."
            )
        )
        self.local_dict = {"pi": math.pi, "e": math.e}

    def run(self, query: str) -> str:
        """Evaluates a mathematical expression securely using numexpr."""
        if not query or not query.strip():
            return "❌ Expression cannot be empty."

        try:
            result = numexpr.evaluate(
                query.strip(),
                global_dict={},            # Secure: no global access
                local_dict=self.local_dict # Allow pi, e
            )
            return str(result.item()) if hasattr(result, "item") else str(result)

        except Exception as e:
            return f"⚠️ Failed to evaluate expression: {str(e)}"


# === For standalone testing ===
if __name__ == "__main__":
    calc_tool = CalculatorTool()
    expressions = [
        "2 + 2",
        "37593 * 67",
        "37593**(1/5)",
        "pi * 2**2",
        "e**2"
    ]

    for expr in expressions:
        answer = calc_tool.run(expr)
        print(f"{expr} = {answer}")
