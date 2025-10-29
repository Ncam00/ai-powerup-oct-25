"""
Test the calculator tools
"""

from calculator_tools import CALCULATOR_TOOLS


def test_basic_operations():
    """Test basic calculator operations"""

    # Test each tool directly
    print("Testing tools directly:")

    # Addition
    result = CALCULATOR_TOOLS[0].invoke({"a": 5, "b": 3})
    print(f"5 + 3 = {result}")

    # Multiplication
    result = CALCULATOR_TOOLS[2].invoke({"a": 4, "b": 6})
    print(f"4 * 6 = {result}")

    # Square root
    result = CALCULATOR_TOOLS[5].invoke({"number": 16})
    print(f"√16 = {result}")

    # Factorial
    result = CALCULATOR_TOOLS[6].invoke({"n": 5})
    print(f"5! = {result}")

    print("\nTool information:")
    for tool in CALCULATOR_TOOLS:
        print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    test_basic_operations()
