"""
Calculator agent that uses tools to solve math problems with Langfuse observability
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from calculator_tools import CALCULATOR_TOOLS

# Import Langfuse for observability
from langfuse.callback import CallbackHandler

load_dotenv()


def get_langfuse_handler():
    """Create Langfuse callback handler for observability"""
    try:
        # Only create handler if API keys are provided
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        
        if secret_key and public_key and not secret_key.endswith("..."):
            langfuse_handler = CallbackHandler(
                secret_key=secret_key,
                public_key=public_key,
                host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
            )
            print("✅ Langfuse observability enabled!")
            return langfuse_handler
        else:
            print("⚠️  Langfuse keys not configured - running without observability")
            return None
    except Exception as e:
        print(f"⚠️  Langfuse setup failed: {e}")
        return None


def create_calculator_agent():
    """Create an LLM that can use calculator tools"""

    # Initialize the LLM with OpenAI (more reliable than Gemini)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        temperature=0
    )

    # Bind the tools to the LLM using bind_tools()
    # This tells the AI what tools are available!
    llm_with_tools = llm.bind_tools(CALCULATOR_TOOLS)

    return llm_with_tools


def solve_math_problem(problem: str):
    """Solve a math problem using the calculator agent with observability"""

    print(f"Problem: {problem}")
    print("-" * 50)

    # Set up Langfuse observability
    langfuse_handler = get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else []

    # Create the agent by calling create_calculator_agent()
    agent = create_calculator_agent()

    # Create a prompt that encourages the AI to use tools
    prompt = f"""
Solve this math problem: {problem}

You have calculator tools available. Use them to perform calculations step by step.
Show your work and explain each step clearly.
Always use the calculator tools rather than doing mental math.
"""

    # Start with the human message
    messages = [HumanMessage(content=prompt)]
    
    # Keep track of iterations to prevent infinite loops
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}")
        
        # Send messages to the agent with observability callbacks
        response = agent.invoke(
            messages, 
            config={
                "callbacks": callbacks,
                "run_name": f"calculator_iteration_{iteration}",
                "metadata": {
                    "problem": problem,
                    "iteration": iteration,
                    "session_type": "math_calculation"
                }
            }
        )
        
        # Add the AI response to our message history
        messages.append(response)
        
        print(f"🤖 AI Response: {response.content}")
        
        # Check if the response contains tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🛠️  Tools called: {len(response.tool_calls)}")
            
            # Process each tool call
            for i, tool_call in enumerate(response.tool_calls):
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                tool_id = tool_call['id']
                
                print(f"   {i+1}. {tool_name}({tool_args})")
                
                # Find and execute the tool
                tool_function = None
                for tool in CALCULATOR_TOOLS:
                    if tool.name == tool_name:
                        tool_function = tool
                        break
                
                if tool_function:
                    try:
                        # Execute the tool and get the result
                        result = tool_function.invoke(tool_args)
                        print(f"      → Result: {result}")
                        
                        # Create a ToolMessage with the result
                        tool_message = ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id
                        )
                        
                        # Add the tool result to our message history
                        messages.append(tool_message)
                        
                    except Exception as e:
                        print(f"      → Error: {e}")
                        # Send error back to AI so it can handle it
                        error_message = ToolMessage(
                            content=f"Error: {e}",
                            tool_call_id=tool_id
                        )
                        messages.append(error_message)
                else:
                    print(f"      → Unknown tool: {tool_name}")
        else:
            # No more tool calls - the AI is done!
            print("✅ Problem solved! No more tools needed.")
            break
    
    if iteration >= max_iterations:
        print("⚠️  Reached maximum iterations - stopping to prevent infinite loop")
    
    if langfuse_handler:
        print("\n📊 Check your Langfuse dashboard for detailed traces!")
        print("   - See token usage and costs")
        print("   - Analyze tool usage patterns") 
        print("   - Debug any issues that occurred")
    
    return response.content
