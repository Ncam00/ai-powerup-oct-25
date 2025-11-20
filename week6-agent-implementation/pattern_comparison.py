"""
Agent Pattern Comparison: Different Approaches to the Same Task

This demonstrates implementing the same task using multiple agent patterns:
1. Augmented LLM - Simple LLM with tools
2. Prompt Chaining - Sequential steps with handoffs
3. Orchestrator-Workers - Dynamic task delegation
4. Autonomous Agent - Self-directed execution (our original implementation)

Task: "Analyze the weather forecast and suggest appropriate clothing"
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
import json

load_dotenv()

# ============================================================================
# SHARED TOOLS (used across all patterns)
# ============================================================================

@tool
def get_weather(location: str) -> str:
    """
    Get current weather for a location.
    
    Args:
        location: City name
    
    Returns:
        Weather information as JSON string
    """
    # Mock weather data
    weather_data = {
        "location": location,
        "temperature": "72°F",
        "condition": "Partly Cloudy",
        "humidity": "65%",
        "wind": "10 mph",
        "precipitation_chance": "20%",
        "uv_index": "Moderate"
    }
    return json.dumps(weather_data, indent=2)


@tool
def suggest_clothing(weather_info: str) -> str:
    """
    Suggest appropriate clothing based on weather.
    
    Args:
        weather_info: JSON string with weather data
    
    Returns:
        Clothing suggestions
    """
    weather = json.loads(weather_info)
    temp = int(weather["temperature"].replace("°F", ""))
    condition = weather["condition"].lower()
    
    suggestions = []
    
    # Temperature-based
    if temp > 80:
        suggestions.append("Light, breathable clothing")
        suggestions.append("Shorts and t-shirt")
    elif temp > 65:
        suggestions.append("Long pants and light shirt")
        suggestions.append("Light jacket optional")
    elif temp > 50:
        suggestions.append("Long pants and sweater")
        suggestions.append("Light jacket recommended")
    else:
        suggestions.append("Warm layers")
        suggestions.append("Heavy coat, hat, gloves")
    
    # Condition-based
    if "rain" in condition or weather["precipitation_chance"].replace("%", "") > "30":
        suggestions.append("Rain jacket or umbrella")
    
    if "sunny" in condition:
        suggestions.append("Sunglasses")
        suggestions.append("Hat for sun protection")
    
    return "\n".join([f"• {s}" for s in suggestions])


# ============================================================================
# PATTERN 1: AUGMENTED LLM
# Simple LLM with direct tool access
# ============================================================================

def pattern1_augmented_llm(location: str) -> str:
    """
    Pattern: Augmented LLM
    - Single LLM call with tool access
    - LLM decides which tools to use
    - Simple and fast
    """
    print("\n" + "="*80)
    print("PATTERN 1: AUGMENTED LLM")
    print("="*80)
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools([get_weather, suggest_clothing])
    
    messages = [
        SystemMessage(content="You are a helpful assistant that provides weather-based clothing advice."),
        HumanMessage(content=f"What should I wear in {location} today?")
    ]
    
    print(f"\nQuery: What should I wear in {location} today?")
    print("\nStep 1: LLM with tools analyzing request...")
    
    # First call - LLM decides to use tools
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        print(f"Step 2: LLM chose to use {len(response.tool_calls)} tool(s)")
        messages.append(response)
        
        # Execute tools
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            print(f"  - Executing: {tool_name}")
            
            if tool_name == "get_weather":
                result = get_weather.invoke(tool_call["args"])
            elif tool_name == "suggest_clothing":
                result = suggest_clothing.invoke(tool_call["args"])
            
            from langchain_core.messages import ToolMessage
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"],
                name=tool_name
            ))
        
        # Second call - LLM synthesizes results
        print("\nStep 3: LLM synthesizing results...")
        final_response = llm_with_tools.invoke(messages)
        result = final_response.content
    else:
        result = response.content
    
    print(f"\nFinal Answer:\n{result}")
    print("\n" + "="*80)
    return result


# ============================================================================
# PATTERN 2: PROMPT CHAINING
# Sequential steps with structured handoffs
# ============================================================================

def pattern2_prompt_chaining(location: str) -> str:
    """
    Pattern: Prompt Chaining
    - Break task into sequential steps
    - Each step has dedicated prompt
    - Output of one feeds into next
    """
    print("\n" + "="*80)
    print("PATTERN 2: PROMPT CHAINING")
    print("="*80)
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    print(f"\nQuery: What should I wear in {location} today?")
    
    # Step 1: Get weather
    print("\nStep 1: Fetching weather data...")
    weather_data = get_weather.invoke({"location": location})
    print(f"Weather: {json.loads(weather_data)['temperature']}, {json.loads(weather_data)['condition']}")
    
    # Step 2: Analyze weather
    print("\nStep 2: Analyzing weather conditions...")
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a weather analyst. Analyze the weather data and identify key factors for clothing decisions."),
        ("human", "Weather data:\n{weather}\n\nWhat are the key factors to consider for clothing?")
    ])
    
    analysis_chain = analysis_prompt | llm
    analysis = analysis_chain.invoke({"weather": weather_data})
    print(f"Analysis: {analysis.content[:100]}...")
    
    # Step 3: Generate clothing suggestions
    print("\nStep 3: Generating clothing suggestions...")
    clothing_data = suggest_clothing.invoke({"weather_info": weather_data})
    
    # Step 4: Format final response
    print("\nStep 4: Formatting final response...")
    format_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a fashion advisor. Create a friendly, conversational response."),
        ("human", """Based on this analysis:
{analysis}

And these clothing suggestions:
{suggestions}

Create a friendly recommendation for what to wear in {location}.""")
    ])
    
    format_chain = format_prompt | llm
    final_response = format_chain.invoke({
        "analysis": analysis.content,
        "suggestions": clothing_data,
        "location": location
    })
    
    result = final_response.content
    print(f"\nFinal Answer:\n{result}")
    print("\n" + "="*80)
    return result


# ============================================================================
# PATTERN 3: ORCHESTRATOR-WORKERS
# Dynamic task breakdown and delegation
# ============================================================================

def pattern3_orchestrator_workers(location: str) -> str:
    """
    Pattern: Orchestrator-Workers
    - Orchestrator breaks down task
    - Workers handle subtasks
    - Orchestrator synthesizes results
    """
    print("\n" + "="*80)
    print("PATTERN 3: ORCHESTRATOR-WORKERS")
    print("="*80)
    
    orchestrator_llm = ChatOpenAI(model="gpt-4", temperature=0)
    worker_llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    
    print(f"\nQuery: What should I wear in {location} today?")
    
    # Orchestrator: Plan the task
    print("\nOrchestrator: Planning task breakdown...")
    orchestrator_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an orchestrator that breaks down tasks.
For clothing advice, identify what subtasks are needed.
Return a JSON list of subtasks with: name, description, tool_needed"""),
        ("human", "Break down the task: Suggest clothing for {location}")
    ])
    
    plan_chain = orchestrator_prompt | orchestrator_llm
    plan = plan_chain.invoke({"location": location})
    print(f"Plan:\n{plan.content}")
    
    # Workers: Execute subtasks
    subtask_results = {}
    
    print("\nWorker 1: Fetching weather data...")
    weather_data = get_weather.invoke({"location": location})
    subtask_results["weather"] = weather_data
    print(f"✓ Weather retrieved")
    
    print("\nWorker 2: Analyzing weather for clothing needs...")
    worker_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a weather-clothing specialist. Analyze weather for clothing decisions."),
        ("human", "Weather data:\n{weather}\n\nWhat clothing factors should we consider?")
    ])
    worker_chain = worker_prompt | worker_llm
    analysis = worker_chain.invoke({"weather": weather_data})
    subtask_results["analysis"] = analysis.content
    print(f"✓ Analysis complete")
    
    print("\nWorker 3: Getting clothing suggestions...")
    clothing = suggest_clothing.invoke({"weather_info": weather_data})
    subtask_results["clothing"] = clothing
    print(f"✓ Suggestions generated")
    
    # Orchestrator: Synthesize results
    print("\nOrchestrator: Synthesizing worker results...")
    synthesis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an orchestrator. Combine worker results into a coherent response."),
        ("human", """Worker results:

Weather Data:
{weather}

Analysis:
{analysis}

Clothing Suggestions:
{clothing}

Create a final recommendation for {location}.""")
    ])
    
    synthesis_chain = synthesis_prompt | orchestrator_llm
    final_response = synthesis_chain.invoke({
        "weather": subtask_results["weather"],
        "analysis": subtask_results["analysis"],
        "clothing": subtask_results["clothing"],
        "location": location
    })
    
    result = final_response.content
    print(f"\nFinal Answer:\n{result}")
    print("\n" + "="*80)
    return result


# ============================================================================
# PATTERN 4: AUTONOMOUS AGENT (from our original implementation)
# Self-directed execution with tool loop
# ============================================================================

def pattern4_autonomous_agent(location: str) -> str:
    """
    Pattern: Autonomous Agent (our LangGraph implementation)
    - Agent decides its own process
    - Uses tools based on environmental feedback
    - Loops until task complete
    """
    print("\n" + "="*80)
    print("PATTERN 4: AUTONOMOUS AGENT (LangGraph)")
    print("="*80)
    
    from agent import run_agent
    
    query = f"What should I wear in {location} today based on the weather?"
    print(f"\nQuery: {query}")
    print("\nAgent executing autonomously...")
    
    result = run_agent(query, max_iterations=5)
    
    final_message = result["messages"][-1]
    answer = final_message.content if hasattr(final_message, 'content') else str(final_message)
    
    print(f"\nFinal Answer:\n{answer}")
    print("\n" + "="*80)
    return answer


# ============================================================================
# COMPARISON RUNNER
# ============================================================================

def run_comparison():
    """Run all patterns and compare results"""
    location = "San Francisco"
    
    print("\n" + "#"*80)
    print("AGENT PATTERN COMPARISON")
    print(f"Task: Suggest clothing for {location}")
    print("#"*80)
    
    results = {}
    
    # Run each pattern
    try:
        results["augmented_llm"] = pattern1_augmented_llm(location)
    except Exception as e:
        results["augmented_llm"] = f"Error: {e}"
    
    try:
        results["prompt_chaining"] = pattern2_prompt_chaining(location)
    except Exception as e:
        results["prompt_chaining"] = f"Error: {e}"
    
    try:
        results["orchestrator_workers"] = pattern3_orchestrator_workers(location)
    except Exception as e:
        results["orchestrator_workers"] = f"Error: {e}"
    
    try:
        results["autonomous_agent"] = pattern4_autonomous_agent(location)
    except Exception as e:
        results["autonomous_agent"] = f"Error: {e}"
    
    # Summary comparison
    print("\n" + "#"*80)
    print("COMPARISON SUMMARY")
    print("#"*80)
    
    print("""
┌─────────────────────────┬──────────┬────────────┬─────────────┬──────────┐
│ Pattern                 │ Speed    │ Complexity │ Flexibility │ Control  │
├─────────────────────────┼──────────┼────────────┼─────────────┼──────────┤
│ 1. Augmented LLM        │ ★★★★★    │ ★☆☆☆☆      │ ★★☆☆☆       │ ★★☆☆☆    │
│ 2. Prompt Chaining      │ ★★★☆☆    │ ★★☆☆☆      │ ★☆☆☆☆       │ ★★★★★    │
│ 3. Orchestrator-Workers │ ★★☆☆☆    │ ★★★★☆      │ ★★★★☆       │ ★★★★☆    │
│ 4. Autonomous Agent     │ ★★★☆☆    │ ★★★☆☆      │ ★★★★★       │ ★★☆☆☆    │
└─────────────────────────┴──────────┴────────────┴─────────────┴──────────┘

KEY INSIGHTS:

Pattern 1: Augmented LLM
✓ Fastest and simplest
✓ Good for straightforward tasks
✗ Less control over execution flow
✗ Limited to single LLM perspective

Pattern 2: Prompt Chaining  
✓ Very predictable and controllable
✓ Clear, debuggable steps
✗ Fixed workflow - no flexibility
✗ More latency due to sequential calls

Pattern 3: Orchestrator-Workers
✓ Great for complex, decomposable tasks
✓ Parallel execution possible
✗ More complex to implement
✗ Higher token usage

Pattern 4: Autonomous Agent
✓ Most flexible - adapts to task
✓ Can handle unexpected scenarios
✗ Less predictable
✗ Requires careful guardrails
    """)
    
    print("\nRECOMMENDATIONS:")
    print("• Simple queries → Augmented LLM")
    print("• Fixed workflows → Prompt Chaining")
    print("• Complex decomposable tasks → Orchestrator-Workers")
    print("• Open-ended exploration → Autonomous Agent")
    
    return results


if __name__ == "__main__":
    run_comparison()
