# Week 6: AI Agent Implementation with LangGraph

## Overview
This implementation demonstrates an autonomous AI agent built with LangGraph (Python framework). The agent can perform multi-step reasoning, use tools to accomplish tasks, and maintain conversation state.

## Agent Capabilities

### Available Tools
1. **Calculator** - Evaluate mathematical expressions
2. **Web Search** - Search the internet for information (mock or real with SERP API)
3. **Current Time** - Get the current date and time

### Core Features
- **Autonomous Decision-Making**: Agent decides which tools to use and when
- **Multi-Step Planning**: Can chain multiple tools to accomplish complex tasks
- **Error Handling**: Graceful recovery from tool execution failures
- **Iteration Control**: Maximum iteration limit to prevent infinite loops
- **Clear Logging**: Detailed logging of all decision-making steps
- **Stateful Conversations**: Maintains context across the entire interaction

## Architecture

### Agent Design Pattern
This implementation follows the **Autonomous Agent** pattern from Anthropic's guide:
- LLM dynamically directs its own processes and tool usage
- Maintains control over how tasks are accomplished
- Uses tools based on environmental feedback in a loop
- Stops when task is complete or max iterations reached

### Graph Structure (LangGraph)
```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐       tool_calls?      ┌─────────┐
│  AGENT  │────────yes────────────▶│  TOOLS  │
│  NODE   │                         │  NODE   │
└────┬────┘                         └────┬────┘
     │                                   │
     │no (final answer)                  │
     │                              ┌────┘
     │                              │
     ▼                              ▼
  ┌─────┐                      (back to agent)
  │ END │
  └─────┘
```

### Components
1. **Agent Node**: Main reasoning component that decides actions
2. **Tool Node**: Executes requested tools and returns results
3. **Conditional Router**: Determines whether to continue or end
4. **State Management**: Tracks messages, iterations, and limits

## Installation

### Prerequisites
```bash
# Python 3.10+
python --version

# Install dependencies
pip install langgraph langchain langchain-openai openai requests python-dotenv
```

### Environment Setup
Create a `.env` file:
```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional: For real web search (otherwise uses mock results)
SERP_API_KEY=your-serpapi-key-here
```

### Getting API Keys

1. **OpenAI API Key** (Required)
   - Sign up at https://platform.openai.com/
   - Navigate to API Keys section
   - Create new secret key

2. **SERP API Key** (Optional)
   - Sign up at https://serpapi.com/
   - Free tier: 100 searches/month
   - Without this key, agent uses mock search results

## Usage

### Running Test Scenarios
```bash
python agent.py
```

This runs 5 pre-configured test cases demonstrating different agent capabilities:
1. Simple calculation
2. Multi-step task (search + calculate)
3. Time query
4. Web search with summarization
5. Complex multi-tool scenario

### Custom Query
```bash
python agent.py "Your question here"
```

Example:
```bash
python agent.py "Search for Python best practices, then calculate 50 * 3 + 12"
```

### Integration in Code
```python
from agent import run_agent

# Simple usage
result = run_agent("What is 25 * 4?")

# With custom iteration limit
result = run_agent("Complex multi-step task...", max_iterations=15)
```

## Example Output

```
================================================================================
STARTING AGENT EXECUTION
================================================================================
Query: What is 15 * 7 + 23?
Max iterations: 10

============================================================
AGENT ITERATION 1
============================================================
Current message count: 1

Agent decision: Use 1 tool(s)
  - calculator: {'expression': '15 * 7 + 23'}

Executing tool: calculator
Arguments: {'expression': '15 * 7 + 23'}
Result: 128

============================================================
AGENT ITERATION 2
============================================================
Current message count: 3

Agent decision: Provide final answer
  Response: The result of 15 * 7 + 23 is 128...

================================================================================
AGENT EXECUTION COMPLETE
================================================================================

Final Answer:
The result of 15 * 7 + 23 is 128.

Total iterations: 2
Total messages: 4
```

## Key Learning Objectives (Week 6)

### ✅ Agent Fundamentals
- Understanding when to use agents vs. simple LLM calls
- Implementing autonomous decision-making with tool selection
- Building agent control flow with state management

### ✅ Tool Integration
- Creating custom tools with clear documentation
- Implementing tool execution with error handling
- Binding tools to LLM for automatic invocation

### ✅ Graph-Based Architecture (LangGraph)
- Building workflows with nodes and edges
- Implementing conditional routing based on agent decisions
- Managing state transitions throughout execution

### ✅ Testing Strategies
- Designing diverse test scenarios for non-deterministic behavior
- Implementing iteration limits for safety
- Logging decision-making process for debugging

### ✅ Error Handling & Safety
- Graceful tool execution failures
- Maximum iteration limits to prevent infinite loops
- Safe evaluation of mathematical expressions
- Clear error messages for troubleshooting

## Agent Design Principles (Anthropic)

This implementation follows best practices from Anthropic's "Building Effective Agents":

1. **✅ Start Simple** - Basic tool set with clear functionality
2. **✅ Maintain Transparency** - All decisions logged and visible
3. **✅ Clear Interfaces** - Well-documented tools with examples
4. **✅ Define Success Criteria** - Iteration limits and completion conditions
5. **✅ Implement Guardrails** - Safe expression evaluation, error handling
6. **✅ Plan for Failure** - Robust error recovery and user-friendly messages

## Comparison to Other Frameworks

### LangGraph (Used Here)
- **Pros**: Graph-based architecture, explicit control flow, LangSmith debugging, persistent checkpoints
- **Cons**: More verbose than higher-level abstractions
- **Best For**: Stateful, long-running workflows with complex orchestration

### Google ADK (Alternative)
- **Pros**: Model-agnostic, built-in evaluation, Vertex AI deployment
- **Cons**: Requires Java or Python, more enterprise-focused
- **Best For**: Production deployment, Google Cloud integration

### Vercel AI SDK (Alternative)
- **Pros**: TypeScript, streaming support, React/Next.js integration
- **Cons**: Primarily for web developers, JavaScript ecosystem
- **Best For**: Web applications with AI-powered features

## Extending This Agent

### Add New Tools
```python
@tool
def your_new_tool(param: str) -> str:
    """
    Clear description of what the tool does.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    """
    # Implementation
    return "result"

# Add to tools list
tools = [calculator, search_web, get_current_time, your_new_tool]
```

### Customize Agent Behavior
```python
# Modify agent system prompt
system_message = SystemMessage(content="""
You are a specialized agent for [domain].
When solving problems, you should:
1. Break down complex tasks into steps
2. Use tools when appropriate
3. Verify results before providing final answers
""")

initial_state = {
    "messages": [system_message, HumanMessage(content=query)],
    "iterations": 0,
    "max_iterations": max_iterations
}
```

### Add Human-in-the-Loop
```python
def human_approval_node(state: AgentState):
    """Request human approval before critical actions"""
    last_message = state["messages"][-1]
    
    if needs_approval(last_message):
        approval = input("Approve this action? (y/n): ")
        if approval.lower() != 'y':
            return {"messages": [AIMessage(content="Action cancelled by user")]}
    
    return state
```

## Testing Agent Behavior

### Unit Tests for Tools
```python
def test_calculator():
    result = calculator.invoke({"expression": "2 + 2"})
    assert result == "4"

def test_calculator_error_handling():
    result = calculator.invoke({"expression": "import os"})
    assert "Error" in result
```

### Integration Tests
```python
def test_agent_simple_calculation():
    result = run_agent("What is 5 * 5?", max_iterations=3)
    assert result is not None
    assert result["iterations"] <= 3
```

### End-State Testing
Focus on outcomes rather than intermediate steps:
```python
def test_agent_accomplishes_task():
    result = run_agent("Calculate 10 + 5 and tell me the time")
    # Check that both tasks were completed
    messages = [m.content for m in result["messages"]]
    assert any("15" in str(m) for m in messages)  # Calculation
    assert any(":" in str(m) for m in messages)   # Time format
```

## Future Enhancements

1. **Persistent Memory**: Save conversation history across sessions
2. **Human-in-the-Loop**: Request approval for critical actions
3. **Multi-Agent Collaboration**: Orchestrator-workers pattern
4. **Advanced Tools**: Database queries, API integrations, file operations
5. **Evaluation Framework**: Automated testing with success metrics
6. **Streaming Responses**: Real-time output for long-running tasks
7. **Cost Tracking**: Monitor token usage and API costs
8. **LangSmith Integration**: Enhanced debugging and tracing

## References
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [Anthropic Agent Patterns Cookbook](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents)

## Week 6 Completion Checklist

### Core Exercises
- ✅ Read Anthropic's multi-agent research and best practices
- ✅ Implemented autonomous agent with LangGraph framework
- ✅ Created 3+ custom tools with proper documentation
- ✅ Added error handling and iteration limits
- ✅ Implemented clear logging of decision-making process
- ✅ Tested with multiple scenarios demonstrating capabilities
- ✅ Followed Anthropic's design principles
- ✅ Documented architecture and usage patterns

### Optional Exercises (ALL COMPLETE!)
- ✅ **Optional #1**: Cloned and analyzed code reviewer demo (Google ADK)
  - See: `CODE_REVIEWER_ANALYSIS.md`
  - Learnings: Sub-agent architecture, risk classification, production patterns
  
- ✅ **Optional #2**: Built comprehensive testing framework
  - See: `test_agent.py` (500+ lines, 40+ tests)
  - Coverage: Unit tests, integration tests, LLM-as-judge, performance, edge cases
  
- ✅ **Optional #3**: Implemented 4 different agent patterns
  - See: `pattern_comparison.py` (400+ lines)
  - Patterns: Augmented LLM, Prompt Chaining, Orchestrator-Workers, Autonomous Agent
  
- ✅ **Optional #4**: Added human-in-the-loop approval workflow
  - See: `human_in_loop.py` (500+ lines)
  - Features: Risk classification, approval workflow, audit trail

### Additional Files
- 📄 **`COMPLETION_SUMMARY.md`** - Comprehensive completion report with learnings
- 📄 **`run_validation.py`** - Simple test runner (no pytest required)

### Stats
- **Total Files**: 8 (4 implementations + 4 docs)
- **Lines of Code**: ~2,250
- **Lines of Documentation**: ~1,000
- **Test Count**: 40+ tests
- **Completion**: 100% (Core + All Optional Exercises)
