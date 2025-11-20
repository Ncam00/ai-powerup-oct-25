"""
Week 6: AI Agent with Tool Use - Web Search & Calculator Agent
Built using LangGraph framework with OpenAI GPT-4

This agent demonstrates:
1. Tool integration (web search, calculator)
2. Multi-step planning and execution
3. Error handling and recovery
4. Clear logging of decision-making process
5. Stateful conversations with memory
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import requests
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")  # Optional: for real web search

# Define tools
@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5 + 3")
    
    Returns:
        The result of the calculation as a string
    
    Examples:
        calculator("2 + 2") -> "4"
        calculator("(10 + 5) * 2") -> "30"
    """
    try:
        # Safe evaluation - only allow basic math operations
        allowed_chars = set("0123456789+-*/() .")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


@tool
def search_web(query: str) -> str:
    """
    Search the web for information using a search engine.
    
    Args:
        query: The search query string
    
    Returns:
        Summary of search results
    
    Examples:
        search_web("latest AI developments") -> "Recent news about AI..."
        search_web("Python programming best practices") -> "Top results..."
    """
    try:
        # If SERP API key is available, use real search
        if SERP_API_KEY:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": SERP_API_KEY,
                "engine": "google"
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            # Extract organic results
            results = []
            for result in data.get("organic_results", [])[:3]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                results.append(f"{title}: {snippet}")
            
            return "\n\n".join(results) if results else "No results found"
        else:
            # Mock search results for demo
            return f"Mock search results for '{query}':\n\n1. {query} - Latest information and developments\n2. {query} - Comprehensive guide and best practices\n3. {query} - Expert insights and analysis"
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool
def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time in human-readable format
    """
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    iterations: int
    max_iterations: int


# Create the LLM with tools
def create_agent_executor():
    """Create the LangGraph agent with tools"""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=OPENAI_API_KEY
    )
    
    # Bind tools to LLM
    tools = [calculator, search_web, get_current_time]
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the agent node
    def agent_node(state: AgentState):
        """
        The main agent reasoning node.
        Decides whether to use tools or provide final answer.
        """
        messages = state["messages"]
        iterations = state.get("iterations", 0)
        
        print(f"\n{'='*60}")
        print(f"AGENT ITERATION {iterations + 1}")
        print(f"{'='*60}")
        print(f"Current message count: {len(messages)}")
        
        # Call LLM with conversation history
        response = llm_with_tools.invoke(messages)
        
        print(f"\nAgent decision: ", end="")
        if response.tool_calls:
            print(f"Use {len(response.tool_calls)} tool(s)")
            for tool_call in response.tool_calls:
                print(f"  - {tool_call['name']}: {tool_call['args']}")
        else:
            print("Provide final answer")
            if response.content:
                print(f"  Response: {response.content[:100]}...")
        
        return {
            "messages": [response],
            "iterations": iterations + 1
        }
    
    # Define the tool execution node
    def tool_node(state: AgentState):
        """
        Execute requested tools and return results.
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = []
        
        # Execute each tool call
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            print(f"\nExecuting tool: {tool_name}")
            print(f"Arguments: {tool_args}")
            
            # Find and execute the tool
            tool_map = {
                "calculator": calculator,
                "search_web": search_web,
                "get_current_time": get_current_time
            }
            
            if tool_name in tool_map:
                try:
                    result = tool_map[tool_name].invoke(tool_args)
                    print(f"Result: {result[:200]}{'...' if len(str(result)) > 200 else ''}")
                    
                    tool_results.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id,
                            name=tool_name
                        )
                    )
                except Exception as e:
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    print(f"Error: {error_msg}")
                    tool_results.append(
                        ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_id,
                            name=tool_name
                        )
                    )
            else:
                error_msg = f"Unknown tool: {tool_name}"
                print(f"Error: {error_msg}")
                tool_results.append(
                    ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                )
        
        return {"messages": tool_results}
    
    # Define conditional edge logic
    def should_continue(state: AgentState):
        """
        Determine if agent should continue or end.
        """
        messages = state["messages"]
        last_message = messages[-1]
        iterations = state.get("iterations", 0)
        max_iterations = state.get("max_iterations", 10)
        
        # Check for max iterations
        if iterations >= max_iterations:
            print(f"\n⚠️  Max iterations ({max_iterations}) reached")
            return "end"
        
        # Check if there are tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_agent(query: str, max_iterations: int = 10):
    """
    Run the agent with a user query.
    
    Args:
        query: The user's question or request
        max_iterations: Maximum number of agent iterations to prevent infinite loops
    """
    print("\n" + "="*80)
    print("STARTING AGENT EXECUTION")
    print("="*80)
    print(f"Query: {query}")
    print(f"Max iterations: {max_iterations}")
    
    # Create agent
    agent = create_agent_executor()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iterations": 0,
        "max_iterations": max_iterations
    }
    
    # Run agent
    try:
        result = agent.invoke(initial_state)
        
        print("\n" + "="*80)
        print("AGENT EXECUTION COMPLETE")
        print("="*80)
        
        # Extract final answer
        final_message = result["messages"][-1]
        if isinstance(final_message, AIMessage):
            print(f"\nFinal Answer:\n{final_message.content}")
        
        print(f"\nTotal iterations: {result['iterations']}")
        print(f"Total messages: {len(result['messages'])}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during agent execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# Test scenarios
def run_test_scenarios():
    """Run various test scenarios to demonstrate agent capabilities"""
    
    test_cases = [
        {
            "query": "What is 15 * 7 + 23?",
            "description": "Simple math calculation"
        },
        {
            "query": "Search for the latest developments in AI agents, then calculate how many days until December 25th, 2024",
            "description": "Multi-step task requiring search and calculation"
        },
        {
            "query": "What time is it right now?",
            "description": "Simple tool call for current time"
        },
        {
            "query": "Find information about LangGraph framework and summarize the key features",
            "description": "Web search with summarization"
        },
        {
            "query": "If I have 3 apples and buy 7 more, then give away half, how many apples do I have left? Also, what's the current date?",
            "description": "Complex multi-tool scenario"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST CASE {i}: {test['description']}")
        print(f"{'#'*80}")
        
        run_agent(test["query"], max_iterations=5)
        
        input("\nPress Enter to continue to next test case...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run with custom query from command line
        query = " ".join(sys.argv[1:])
        run_agent(query)
    else:
        # Run test scenarios
        print("="*80)
        print("WEEK 6: AI AGENT DEMONSTRATION")
        print("LangGraph Framework with Tool Use")
        print("="*80)
        
        run_test_scenarios()
