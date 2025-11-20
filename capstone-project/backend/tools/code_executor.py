"""
Code Execution Tool
===================

Week 3: Tool use for safe Python code execution
"""

from langchain_core.tools import tool
import ast
import sys
from io import StringIO
import signal
from contextlib import contextmanager
import logging

from api.models.config import settings

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    """Raised when code execution times out"""
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timeouts"""
    def timeout_handler(signum, frame):
        raise TimeoutException("Code execution timed out")
    
    # Set the timeout handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def is_safe_code(code: str) -> tuple[bool, str]:
    """
    Check if code is safe to execute
    
    Returns:
        (is_safe, error_message)
    """
    
    # Check for dangerous imports
    dangerous_patterns = [
        'import os', 'import sys', 'import subprocess',
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file(', '__builtins__'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return False, f"Restricted pattern detected: {pattern}"
    
    # Parse AST to check imports
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in settings.ALLOWED_IMPORTS:
                    return False, f"Import not allowed: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module not in settings.ALLOWED_IMPORTS:
                return False, f"Import not allowed: {node.module}"
    
    return True, ""

@tool
def execute_python_code(code: str) -> str:
    """
    Execute Python code safely in a sandboxed environment.
    
    Use this tool when the student wants to run code or see output.
    Maximum execution time: 5 seconds.
    Only standard library imports allowed.
    
    Args:
        code: Python code to execute
    
    Returns:
        Output from code execution or error message
    
    Examples:
        >>> execute_python_code("print(2 + 2)")
        "4"
        
        >>> execute_python_code("for i in range(3): print(i)")
        "0\\n1\\n2"
    """
    
    logger.info(f"Executing code: {code[:100]}...")
    
    # Safety check
    is_safe, error = is_safe_code(code)
    if not is_safe:
        return f"❌ Security Error: {error}"
    
    # Length check
    if len(code) > settings.MAX_CODE_LENGTH:
        return f"❌ Error: Code too long (max {settings.MAX_CODE_LENGTH} characters)"
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        # Execute with timeout
        with timeout(settings.CODE_TIMEOUT_SECONDS):
            # Create restricted globals
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'range': range,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'any': any,
                    'all': all,
                }
            }
            
            # Execute code
            exec(code, restricted_globals)
            
            # Get output
            output = captured_output.getvalue()
            
            if output:
                return f"✅ Output:\n{output}"
            else:
                return "✅ Code executed successfully (no output)"
    
    except TimeoutException:
        return f"❌ Timeout: Code took longer than {settings.CODE_TIMEOUT_SECONDS} seconds"
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        return f"❌ {error_type}: {error_msg}"
    
    finally:
        sys.stdout = old_stdout

@tool
def test_code_with_cases(code: str, test_cases: str) -> str:
    """
    Test Python code with specific test cases.
    
    Use this to verify if student code works correctly.
    
    Args:
        code: Python code (should define a function)
        test_cases: Test cases as string (e.g., "assert func(1) == 2")
    
    Returns:
        Test results
    
    Example:
        >>> test_code_with_cases(
        ...     "def add(a, b): return a + b",
        ...     "assert add(2, 3) == 5\\nassert add(0, 0) == 0"
        ... )
        "✅ All tests passed!"
    """
    
    full_code = code + "\n\n" + test_cases
    
    is_safe, error = is_safe_code(full_code)
    if not is_safe:
        return f"❌ Security Error: {error}"
    
    try:
        # Execute code and tests
        exec_globals = {}
        exec(full_code, exec_globals)
        return "✅ All tests passed!"
    
    except AssertionError as e:
        return f"❌ Test Failed: {e}"
    
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"
