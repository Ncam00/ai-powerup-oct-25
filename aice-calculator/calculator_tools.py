"""
Calculator tools for LangChain
"""

from langchain_core.tools import tool
import math


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first number."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide the first number by the second number."""
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b


@tool
def power(base: float, exponent: float) -> float:
    """Raise a number to the power of another number."""
    return base**exponent


@tool
def square_root(number: float) -> float:
    """Calculate the square root of a number."""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number!")
    return math.sqrt(number)


@tool
def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers!")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# Collect all tools in a list for easy access
CALCULATOR_TOOLS = [add, subtract, multiply, divide, power, square_root, factorial]
