"""
Learning Tools for PythonMentor AI using LangChain tools
"""

from langchain_core.tools import tool
import subprocess
import tempfile
import os
import sys
from typing import Dict, Any
import traceback

@tool
def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code safely and return the output.
    Useful for demonstrating code examples and letting students test their code.
    """
    try:
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code and capture output
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10  # 10-second timeout for safety
        )
        
        # Clean up
        os.unlink(temp_file)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Code execution timed out (10 seconds limit)",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "exit_code": -1
        }

@tool  
def validate_python_syntax(code: str) -> Dict[str, Any]:
    """
    Check if Python code has valid syntax without executing it.
    Useful for checking student code before execution.
    """
    try:
        # Try to compile the code
        compile(code, '<string>', 'exec')
        return {
            "valid": True,
            "error_message": None,
            "suggestions": []
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error_message": f"Syntax error at line {e.lineno}: {e.msg}",
            "suggestions": [
                "Check for missing colons after if/for/while/def statements",
                "Verify proper indentation",
                "Make sure parentheses and brackets are balanced"
            ]
        }
    except Exception as e:
        return {
            "valid": False,
            "error_message": f"Code validation error: {str(e)}",
            "suggestions": []
        }

@tool
def explain_python_error(error_message: str) -> str:
    """
    Provide beginner-friendly explanations for common Python errors.
    Helps students understand what went wrong and how to fix it.
    """
    error_explanations = {
        "NameError": "This means you're trying to use a variable that hasn't been defined yet. Make sure you've created the variable before using it.",
        "IndentationError": "Python uses indentation (spaces/tabs) to group code. Make sure your code is properly indented, especially after if, for, while, and def statements.",
        "SyntaxError": "There's a problem with how you've written the code. Check for missing colons, unmatched parentheses, or typos in keywords.",
        "TypeError": "You're trying to do something with a data type that doesn't support that operation. For example, adding a string to a number.",
        "IndexError": "You're trying to access a position in a list that doesn't exist. Remember, lists start counting from 0!",
        "KeyError": "You're trying to access a dictionary key that doesn't exist. Use 'in' to check if a key exists first.",
        "ValueError": "The function received the right type of data but an inappropriate value. For example, trying to convert 'hello' to an integer.",
        "FileNotFoundError": "Python can't find the file you're trying to open. Check the file path and make sure the file exists.",
        "ZeroDivisionError": "You're trying to divide by zero, which is mathematically impossible!"
    }
    
    # Find matching error type
    for error_type, explanation in error_explanations.items():
        if error_type in error_message:
            return f"**{error_type}**: {explanation}\\n\\nOriginal error: {error_message}"
    
    # Generic explanation if no specific match found
    return f"I see you got an error: {error_message}\\n\\nThis looks like something we can debug together! Can you show me the code that caused this error?"

@tool
def suggest_learning_topics(current_level: str, topics_covered: list) -> Dict[str, Any]:
    """
    Suggest next learning topics based on student's current level and progress.
    Provides personalized learning path recommendations.
    """
    learning_paths = {
        "beginner": [
            {"topic": "Variables and Data Types", "priority": 1, "description": "Learn about integers, strings, floats, and booleans"},
            {"topic": "Basic Input/Output", "priority": 2, "description": "Using print() and input() functions"},
            {"topic": "Conditional Statements", "priority": 3, "description": "if, elif, else statements"},
            {"topic": "Loops", "priority": 4, "description": "for and while loops"},
            {"topic": "Lists", "priority": 5, "description": "Creating and manipulating lists"},
            {"topic": "Functions", "priority": 6, "description": "Defining and calling functions"},
        ],
        "intermediate": [
            {"topic": "Dictionaries", "priority": 1, "description": "Key-value data structures"},
            {"topic": "List Comprehensions", "priority": 2, "description": "Concise way to create lists"},
            {"topic": "Error Handling", "priority": 3, "description": "try, except, finally blocks"},
            {"topic": "File Operations", "priority": 4, "description": "Reading and writing files"},
            {"topic": "Classes and Objects", "priority": 5, "description": "Object-oriented programming basics"},
            {"topic": "Modules and Packages", "priority": 6, "description": "Organizing code and using libraries"},
        ],
        "advanced": [
            {"topic": "Decorators", "priority": 1, "description": "Functions that modify other functions"},
            {"topic": "Generators", "priority": 2, "description": "Memory-efficient iterators"},
            {"topic": "Context Managers", "priority": 3, "description": "with statements and resource management"},
            {"topic": "Advanced OOP", "priority": 4, "description": "Inheritance, polymorphism, magic methods"},
            {"topic": "Testing", "priority": 5, "description": "unittest, pytest, and testing best practices"},
            {"topic": "Performance Optimization", "priority": 6, "description": "Profiling and optimizing Python code"},
        ]
    }
    
    level_topics = learning_paths.get(current_level, learning_paths["beginner"])
    
    # Filter out already covered topics
    covered_set = set(topic.lower() for topic in topics_covered)
    suggested_topics = []
    
    for topic_info in level_topics:
        if topic_info["topic"].lower() not in covered_set:
            suggested_topics.append(topic_info)
            if len(suggested_topics) >= 3:  # Suggest top 3 topics
                break
    
    return {
        "suggested_topics": suggested_topics,
        "current_level": current_level,
        "total_topics_covered": len(topics_covered),
        "learning_progress": f"{len(topics_covered)}/{len(level_topics)} topics completed for {current_level} level"
    }

@tool
def create_coding_exercise(topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Generate a coding exercise for a specific topic and difficulty level.
    Helps provide hands-on practice for students.
    """
    exercises = {
        "variables": {
            "beginner": {
                "title": "Personal Information Storage",
                "description": "Create variables to store your name, age, and favorite color, then print them in a sentence.",
                "starter_code": "# Create variables for your personal information\\nname = \\nage = \\nfavorite_color = \\n\\n# Print a sentence using these variables",
                "expected_concepts": ["variable assignment", "string concatenation", "print function"]
            }
        },
        "functions": {
            "beginner": {
                "title": "Simple Calculator Function",
                "description": "Write a function that takes two numbers and returns their sum.",
                "starter_code": "def add_numbers(a, b):\\n    # Your code here\\n    pass\\n\\n# Test your function\\nresult = add_numbers(5, 3)\\nprint(result)",
                "expected_concepts": ["function definition", "parameters", "return statement"]
            }
        },
        "loops": {
            "beginner": {
                "title": "Counting Exercise",
                "description": "Use a for loop to print numbers from 1 to 10.",
                "starter_code": "# Write a for loop to print numbers 1 to 10\\nfor i in range(?):\\n    print(?)",
                "expected_concepts": ["for loops", "range function", "loop variables"]
            }
        }
    }
    
    topic_lower = topic.lower()
    if topic_lower in exercises and difficulty in exercises[topic_lower]:
        exercise = exercises[topic_lower][difficulty]
        return {
            "success": True,
            "exercise": exercise,
            "topic": topic,
            "difficulty": difficulty
        }
    else:
        return {
            "success": False,
            "message": f"No exercise found for topic '{topic}' at '{difficulty}' level",
            "available_topics": list(exercises.keys())
        }

# Collect all tools for easy access
PYTHON_LEARNING_TOOLS = [
    execute_python_code,
    validate_python_syntax, 
    explain_python_error,
    suggest_learning_topics,
    create_coding_exercise
]