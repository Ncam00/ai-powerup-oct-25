"""
Week 3 Deep Dive: Advanced Custom Tools Architecture
Exploring tool chaining, error handling, async tools, and composition patterns
"""

import asyncio
import json
import tempfile
import subprocess
import time
from functools import wraps
from typing import Dict, Any, List, Optional, Union, Callable
from langchain_core.tools import tool, StructuredTool
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel, Field
import logging


# Configure logging for tool operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Structured result from tool execution"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}


class ToolMetrics(BaseModel):
    """Metrics for tool performance tracking"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0


# Global metrics storage
TOOL_METRICS: Dict[str, ToolMetrics] = {}


def track_performance(func: Callable) -> Callable:
    """Decorator to track tool performance metrics"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        # Initialize metrics if not exists
        if tool_name not in TOOL_METRICS:
            TOOL_METRICS[tool_name] = ToolMetrics()
        
        metrics = TOOL_METRICS[tool_name]
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Update metrics
            metrics.total_calls += 1
            metrics.successful_calls += 1
            metrics.total_execution_time += execution_time
            metrics.average_execution_time = metrics.total_execution_time / metrics.total_calls
            
            logger.info(f"Tool {tool_name} executed successfully in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update metrics
            metrics.total_calls += 1
            metrics.failed_calls += 1
            metrics.total_execution_time += execution_time
            metrics.average_execution_time = metrics.total_execution_time / metrics.total_calls
            
            logger.error(f"Tool {tool_name} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    return wrapper


def safe_execution(default_return=None, log_errors=True):
    """Decorator for safe tool execution with error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


# ===== BASIC ENHANCED TOOLS =====

@tool
@track_performance
@safe_execution(default_return="Error in calculation")
def enhanced_calculator(expression: str) -> str:
    """
    Advanced calculator with error handling and safety checks.
    Supports basic arithmetic, parentheses, and common math functions.
    """
    # Sanitize input to prevent code injection
    allowed_chars = set('0123456789+-*/().() ')
    allowed_functions = ['sin', 'cos', 'tan', 'sqrt', 'log', 'abs', 'pow']
    
    # Basic safety check
    if not all(c in allowed_chars or any(f in expression for f in allowed_functions) for c in expression):
        raise ValueError("Invalid characters in expression")
    
    try:
        # Use eval with restricted globals for safety
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "pow": pow,
            "round": round,
        }
        
        # Import math functions safely
        import math
        safe_dict.update({
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "pi": math.pi,
            "e": math.e
        })
        
        result = eval(expression, safe_dict, {})
        return f"Result: {result}"
        
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
@track_performance
def text_analysis_tool(text: str, analysis_type: str = "summary") -> str:
    """
    Advanced text analysis tool with multiple analysis types.
    Types: summary, word_count, sentiment, readability
    """
    text = text.strip()
    
    if analysis_type == "word_count":
        words = len(text.split())
        chars = len(text)
        sentences = text.count('.') + text.count('!') + text.count('?')
        return f"Words: {words}, Characters: {chars}, Sentences: {sentences}"
    
    elif analysis_type == "summary":
        # Simple extractive summary (first sentence + key stats)
        first_sentence = text.split('.')[0] + '.'
        words = len(text.split())
        return f"Summary: {first_sentence} (Total: {words} words)"
    
    elif analysis_type == "sentiment":
        # Basic sentiment analysis using keyword counting
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return f"Sentiment: Positive (pos: {pos_count}, neg: {neg_count})"
        elif neg_count > pos_count:
            return f"Sentiment: Negative (pos: {pos_count}, neg: {neg_count})"
        else:
            return f"Sentiment: Neutral (pos: {pos_count}, neg: {neg_count})"
    
    elif analysis_type == "readability":
        # Simple readability score based on word and sentence length
        words = text.split()
        sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
        avg_words_per_sentence = len(words) / sentences
        avg_chars_per_word = sum(len(word) for word in words) / max(1, len(words))
        
        return f"Readability: {avg_words_per_sentence:.1f} words/sentence, {avg_chars_per_word:.1f} chars/word"
    
    else:
        return f"Unknown analysis type: {analysis_type}"


# ===== ASYNC TOOLS =====

@tool
async def async_web_research(query: str, max_results: int = 3) -> str:
    """
    Simulated async web research tool.
    In production, this would make actual HTTP requests.
    """
    # Simulate async operation
    await asyncio.sleep(0.5)
    
    # Simulate search results
    results = [
        f"Search result {i+1} for '{query}': Lorem ipsum research finding..."
        for i in range(max_results)
    ]
    
    return f"Research results for '{query}':\n" + "\n".join(f"{i+1}. {result}" for i, result in enumerate(results))


@tool
async def async_code_formatter(code: str, language: str = "python") -> str:
    """
    Async code formatting tool.
    Simulates formatting code with external service.
    """
    await asyncio.sleep(0.2)  # Simulate processing time
    
    # Simple formatting simulation
    lines = code.strip().split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Decrease indent for closing brackets
        if stripped.startswith((')', '}', ']')):
            indent_level = max(0, indent_level - 1)
        
        # Add formatted line
        formatted_lines.append('    ' * indent_level + stripped)
        
        # Increase indent for opening brackets
        if stripped.endswith((':', '{', '(')):
            indent_level += 1
    
    return f"Formatted {language} code:\n```{language}\n" + '\n'.join(formatted_lines) + "\n```"


# ===== TOOL COMPOSITION AND CHAINING =====

class ToolChain:
    """Chain multiple tools together for complex operations"""
    
    def __init__(self):
        self.tools = []
        self.results = []
    
    def add_tool(self, tool_func: Callable, **kwargs):
        """Add a tool to the chain"""
        self.tools.append((tool_func, kwargs))
        return self
    
    def execute(self, input_data: str) -> List[ToolResult]:
        """Execute the tool chain"""
        current_input = input_data
        
        for tool_func, kwargs in self.tools:
            start_time = time.time()
            
            try:
                # Execute tool with current input
                if 'input' in tool_func.func.__code__.co_varnames:
                    result = tool_func.func(current_input, **kwargs)
                else:
                    # Assume first parameter is the input
                    result = tool_func.func(current_input, **kwargs)
                
                execution_time = time.time() - start_time
                
                tool_result = ToolResult(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    metadata={"tool_name": tool_func.name}
                )
                
                self.results.append(tool_result)
                current_input = str(result)  # Output becomes next input
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                tool_result = ToolResult(
                    success=False,
                    error=str(e),
                    execution_time=execution_time,
                    metadata={"tool_name": tool_func.name}
                )
                
                self.results.append(tool_result)
                break  # Stop chain on error
        
        return self.results


# ===== SPECIALIZED TOOLS =====

@tool
@track_performance
def file_operations_tool(operation: str, filename: str, content: str = "") -> str:
    """
    Safe file operations tool with restricted access.
    Operations: create, read, append, list_dir
    """
    # Security: Only allow operations in temp directory
    if not filename.startswith("/tmp/") and not filename.startswith("temp_"):
        return "Error: File operations restricted to temp directories for security"
    
    try:
        if operation == "create":
            with open(filename, 'w') as f:
                f.write(content)
            return f"File {filename} created successfully"
        
        elif operation == "read":
            with open(filename, 'r') as f:
                content = f.read()
            return f"File content:\n{content}"
        
        elif operation == "append":
            with open(filename, 'a') as f:
                f.write(content)
            return f"Content appended to {filename}"
        
        elif operation == "list_dir":
            import os
            files = os.listdir(os.path.dirname(filename) or "/tmp")
            return f"Files in directory: {', '.join(files)}"
        
        else:
            return f"Unknown operation: {operation}"
    
    except Exception as e:
        return f"File operation error: {str(e)}"


@tool
@track_performance
def data_processing_tool(data: str, operation: str, format_type: str = "json") -> str:
    """
    Advanced data processing tool.
    Operations: parse, validate, transform, aggregate
    """
    try:
        if format_type == "json":
            # Try to parse as JSON
            if operation == "parse":
                parsed = json.loads(data)
                return f"Parsed JSON with {len(parsed)} items" if isinstance(parsed, list) else "Parsed JSON object"
            
            elif operation == "validate":
                json.loads(data)  # Will throw exception if invalid
                return "Valid JSON format"
            
            elif operation == "transform":
                parsed = json.loads(data)
                # Simple transformation: convert all string values to uppercase
                if isinstance(parsed, dict):
                    transformed = {k: v.upper() if isinstance(v, str) else v for k, v in parsed.items()}
                elif isinstance(parsed, list):
                    transformed = [item.upper() if isinstance(item, str) else item for item in parsed]
                else:
                    transformed = parsed
                return json.dumps(transformed, indent=2)
        
        elif format_type == "csv":
            lines = data.strip().split('\n')
            if operation == "parse":
                return f"CSV data with {len(lines)} rows"
            elif operation == "validate":
                # Check if all rows have same number of columns
                if lines:
                    expected_cols = len(lines[0].split(','))
                    for i, line in enumerate(lines[1:], 1):
                        if len(line.split(',')) != expected_cols:
                            return f"Invalid CSV: Row {i} has different column count"
                return "Valid CSV format"
        
        return f"Operation {operation} completed on {format_type} data"
        
    except Exception as e:
        return f"Data processing error: {str(e)}"


# ===== TOOL METRICS AND REPORTING =====

@tool
def get_tool_metrics(tool_name: str = "all") -> str:
    """Get performance metrics for tools"""
    if tool_name == "all":
        if not TOOL_METRICS:
            return "No tool metrics available"
        
        report = "Tool Performance Report:\n" + "=" * 30 + "\n"
        for name, metrics in TOOL_METRICS.items():
            success_rate = (metrics.successful_calls / metrics.total_calls * 100) if metrics.total_calls > 0 else 0
            report += f"{name}:\n"
            report += f"  Total calls: {metrics.total_calls}\n"
            report += f"  Success rate: {success_rate:.1f}%\n"
            report += f"  Avg execution time: {metrics.average_execution_time:.3f}s\n\n"
        
        return report
    
    elif tool_name in TOOL_METRICS:
        metrics = TOOL_METRICS[tool_name]
        success_rate = (metrics.successful_calls / metrics.total_calls * 100) if metrics.total_calls > 0 else 0
        return f"Metrics for {tool_name}:\nCalls: {metrics.total_calls}, Success: {success_rate:.1f}%, Avg time: {metrics.average_execution_time:.3f}s"
    
    else:
        return f"No metrics found for tool: {tool_name}"


# ===== ADVANCED TOOL SYSTEM =====

ALL_ADVANCED_TOOLS = [
    enhanced_calculator,
    text_analysis_tool,
    async_web_research,
    async_code_formatter,
    file_operations_tool,
    data_processing_tool,
    get_tool_metrics
]


def demonstrate_advanced_tools():
    """Demonstrate advanced tool capabilities"""
    print("🛠️ Advanced Tools Architecture Demo")
    print("=" * 50)
    
    # Test 1: Enhanced calculator with tracking
    print("\n1. Enhanced Calculator with Performance Tracking:")
    calc_result = enhanced_calculator.func("2 + 3 * 4 - sqrt(16)")
    print(f"Calculator result: {calc_result}")
    
    # Test 2: Text analysis
    print("\n2. Text Analysis Tool:")
    sample_text = "This is a great example of text analysis. The tool works wonderfully and provides excellent insights!"
    
    for analysis_type in ["word_count", "sentiment", "readability"]:
        result = text_analysis_tool.func(sample_text, analysis_type)
        print(f"  {analysis_type}: {result}")
    
    # Test 3: Tool chaining
    print("\n3. Tool Chain Demonstration:")
    chain = ToolChain()
    chain.add_tool(text_analysis_tool, analysis_type="word_count")
    
    text_input = "Advanced tool systems enable powerful AI applications with robust error handling."
    chain_results = chain.execute(text_input)
    
    for i, result in enumerate(chain_results):
        print(f"  Step {i+1}: {'✅' if result.success else '❌'} {result.result or result.error}")
    
    # Test 4: Data processing
    print("\n4. Data Processing Tool:")
    json_data = '{"name": "john", "age": 30, "city": "new york"}'
    
    parse_result = data_processing_tool.func(json_data, "parse", "json")
    print(f"  Parse: {parse_result}")
    
    transform_result = data_processing_tool.func(json_data, "transform", "json")
    print(f"  Transform: {transform_result[:100]}...")
    
    # Test 5: Performance metrics
    print("\n5. Tool Performance Metrics:")
    metrics_report = get_tool_metrics.func("all")
    print(metrics_report)
    
    print("\n📊 Advanced Tool Features Demonstrated:")
    print("• Performance tracking with decorators")
    print("• Safe execution with error handling")
    print("• Tool chaining for complex operations")
    print("• Async tool support (simulated)")
    print("• Data validation and processing")
    print("• Comprehensive metrics and reporting")
    print("• Security restrictions for file operations")


if __name__ == "__main__":
    demonstrate_advanced_tools()