# Week 3: Tool Use Challenge - Enhanced Calculator Agent

This directory demonstrates Week 3's **Tool Use Challenge** with advanced LangChain tool integration and multi-step problem solving.

## 🎯 Learning Objectives

- **Tool Definition**: Create custom tools using LangChain's `@tool` decorator
- **Tool Chaining**: Chain multiple tools together for complex problem solving
- **Agent Patterns**: Build AI agents that can use tools autonomously
- **Problem Decomposition**: Break complex problems into tool-executable steps

## 🚀 What This Demonstrates

### Core Tool Use Concepts
1. **@tool Decorator**: Define tools with automatic schema generation
2. **Tool Composition**: Chain multiple tools for multi-step solutions
3. **State Management**: Track results between tool calls
4. **Error Handling**: Graceful fallbacks for tool execution failures

### Advanced Patterns
- **Problem Analysis**: Parse natural language into executable steps
- **Tool Selection**: Choose appropriate tools based on problem type
- **Result Chaining**: Pass outputs from one tool as inputs to another
- **Audit Trails**: Maintain history of tool calls and results

## 🔧 Implementation Highlights

### Tool Definition Pattern
```python
@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

# Tools are automatically converted to LangChain tools with:
# - Schema generation from type hints
# - Documentation from docstrings
# - Input validation
```

### Multi-Step Problem Solving
```python
class CalculatorAgent:
    def solve_problem(self, problem: str):
        steps = self._analyze_problem(problem)
        
        for step in steps:
            if step['tool_needed']:
                result = self._execute_tool_call(step)
                # Chain results to next step
        
        return final_answer
```

### Tool Categories Implemented
- **Basic Arithmetic**: add, subtract, multiply, divide
- **Advanced Math**: power, square_root, factorial
- **Problem Types**: Order of operations, compound expressions, chained calculations

## 📊 Demo Scenarios

The enhanced calculator handles complex multi-step problems:

1. **Chained Operations**: "Square root of 144 then multiply by 5"
2. **Multiple Tools**: "Factorial of 5 plus factorial of 4"
3. **Order of Operations**: "2 + 3 * 4^2"
4. **Compound Powers**: "2^3^2"

Each problem demonstrates:
- Automatic problem decomposition
- Sequential tool execution
- Result passing between steps
- Complete audit trail

## 🎓 Week 3 Skills Mastered

✅ **Tool Definition** - Using `@tool` decorator with type hints and validation  
✅ **Tool Chaining** - Connecting multiple tools for complex workflows  
✅ **Problem Decomposition** - Breaking problems into tool-executable steps  
✅ **State Management** - Tracking intermediate results and tool call history  
✅ **Error Handling** - Graceful fallbacks and validation  

## 🔄 Integration with Week 3 Goals

This tool use implementation prepares for:
1. **Langfuse Observability** - Ready to add tracing to tool calls
2. **Structured Output** - Tool results can be structured with Pydantic
3. **Real LLM Integration** - Framework ready for actual LLM-powered agents

## 🚀 Real-World Applications

This pattern extends to:
- **API Tools**: Web service integration
- **Database Tools**: Query and update operations  
- **File Tools**: Reading, writing, processing files
- **Analysis Tools**: Data processing and visualization

---

*This implementation showcases Week 3's focus on building robust AI applications with proper tool use patterns and evaluation frameworks.*