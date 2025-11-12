"""
Calculator agent that uses tools to solve math problems with Langfuse observability
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from calculator_tools import CALCULATOR_TOOLS

# Import Langfuse for observability
try:
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    CallbackHandler = None

load_dotenv()


def get_langfuse_handler():
    """Create Langfuse callback handler for observability"""
    if not LANGFUSE_AVAILABLE:
        return None
        
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


def get_enhanced_prompt(problem: str, iteration: int = 1) -> str:
    """Generate an advanced prompt based on problem complexity and iteration"""
    
    # Analyze problem complexity
    complexity_indicators = {
        'simple': any(op in problem.lower() for op in ['what is', 'calculate', '+', '-', '*', '/']),
        'intermediate': any(op in problem.lower() for op in ['square root', 'power', 'factorial', 'order of operations']),
        'complex': any(term in problem.lower() for term in ['step by step', 'multi-step', 'solve for', 'equation'])
    }
    
    # Base persona and role
    base_prompt = """🧮 You are an EXPERT MATHEMATICAL ASSISTANT with access to precision calculator tools.

📋 YOUR MISSION:
Solve the given math problem with PERFECT ACCURACY using available tools.

🎯 CORE PRINCIPLES:
1. NEVER do mental math - ALWAYS use calculator tools for ANY computation
2. Break complex problems into clear, logical steps
3. Explain your reasoning before each calculation
4. Verify results make sense in context
5. Show your work clearly for educational value
"""
    
    # Problem-specific guidance
    if iteration == 1:
        problem_analysis = f"""
📊 PROBLEM TO SOLVE: {problem}

🔍 ANALYSIS FRAMEWORK:
1. First, identify what type of calculation this requires
2. Break down the problem into individual operations
3. Determine the correct order of operations if needed
4. Execute each step using appropriate calculator tools
5. Present the final answer with clear reasoning
"""
    else:
        problem_analysis = f"""
🔄 ITERATION {iteration}: Continue solving: {problem}

Note: You've already made progress. Build on previous calculations.
"""
    
    # Tool usage guidelines
    tool_guidance = """
🛠️ AVAILABLE TOOLS & WHEN TO USE:
• add(a, b) - For any addition operation
• subtract(a, b) - For any subtraction operation  
• multiply(a, b) - For any multiplication operation
• divide(a, b) - For any division operation
• power(base, exponent) - For exponentiation (x^y, "to the power of")
• square_root(number) - For square roots (√x)
• factorial(n) - For factorials (n!)

⚠️ CRITICAL TOOL USAGE RULES:
- Use tools for EVERY calculation, no matter how simple
- For order of operations, break into individual tool calls
- If a tool fails, explain the error and try alternative approaches
- Double-check results by using tools for verification
"""
    
    # Response format
    format_guide = """
📝 RESPONSE FORMAT:
1. **Problem Understanding**: Restate what you need to solve
2. **Solution Strategy**: Outline your step-by-step approach
3. **Calculations**: Execute each step with tool calls
4. **Final Answer**: State the result clearly with units if applicable
5. **Verification**: Confirm the answer makes sense

✅ EXAMPLE INTERACTION:
"I need to solve: What is 15 + 27?

Strategy: This is a simple addition problem.
Step 1: Use the add tool to compute 15 + 27
[Tool call: add(15, 27)]
Result: 42

Final Answer: 15 + 27 = 42
Verification: This seems reasonable as both numbers are positive."
"""
    
    return f"{base_prompt}\n{problem_analysis}\n{tool_guidance}\n{format_guide}"


def solve_math_problem(problem: str):
    """Solve a math problem using enhanced prompting with the calculator agent"""

    print(f"Problem: {problem}")
    print("-" * 50)

    # Set up Langfuse observability
    langfuse_handler = get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else []

    # Create the agent by calling create_calculator_agent()
    agent = create_calculator_agent()

    # Keep track of iterations to prevent infinite loops
    max_iterations = 8  # Reduced for efficiency
    iteration = 0
    
    # Start with enhanced prompt
    enhanced_prompt = get_enhanced_prompt(problem, 1)
    messages = [HumanMessage(content=enhanced_prompt)]
    
    # Track tool usage patterns to detect issues
    tool_usage_history = []
    repeated_calls_threshold = 3
    
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
                
                # Track tool usage for pattern detection
                tool_call_signature = f"{tool_name}({tool_args})"
                tool_usage_history.append(tool_call_signature)
                
                # Check for repeated identical calls
                recent_calls = tool_usage_history[-repeated_calls_threshold:]
                if len(recent_calls) == repeated_calls_threshold and all(call == tool_call_signature for call in recent_calls):
                    print(f"      ⚠️ Detected repeated tool call: {tool_call_signature}")
                    error_message = ToolMessage(
                        content=f"Error: Detected repeated calculation {tool_call_signature}. Consider if this calculation is necessary or if the problem is already solved.",
                        tool_call_id=tool_id
                    )
                    messages.append(error_message)
                    continue
                
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
                        
                        # Create enhanced tool result message
                        result_message = f"Calculation completed: {tool_name}({tool_args}) = {result}"
                        tool_message = ToolMessage(
                            content=result_message,
                            tool_call_id=tool_id
                        )
                        
                        # Add the tool result to our message history
                        messages.append(tool_message)
                        
                    except Exception as e:
                        print(f"      → Error: {e}")
                        # Provide detailed error guidance
                        error_guidance = f"""Error in {tool_name}: {e}
                        
Troubleshooting suggestions:
- Check if arguments are valid numbers
- For division, ensure denominator is not zero
- For square_root, ensure number is non-negative
- For factorial, ensure number is non-negative integer
- Consider breaking complex expressions into simpler steps"""
                        
                        error_message = ToolMessage(
                            content=error_guidance,
                            tool_call_id=tool_id
                        )
                        messages.append(error_message)
                else:
                    print(f"      → Unknown tool: {tool_name}")
                    # Guide AI to available tools
                    available_tools = [tool.name for tool in CALCULATOR_TOOLS]
                    guidance_message = ToolMessage(
                        content=f"Unknown tool '{tool_name}'. Available tools: {', '.join(available_tools)}. Please use one of these tools instead.",
                        tool_call_id=tool_id
                    )
                    messages.append(guidance_message)
        else:
            # No more tool calls - analyze if problem is actually solved
            if iteration == 1:
                # First iteration with no tools might indicate the AI thinks it can solve without tools
                print("⚠️  AI didn't use any tools on first attempt - encouraging tool usage...")
                reminder_message = HumanMessage(
                    content="""Remember: You MUST use the calculator tools for ANY numerical computation. 
                    Please solve the problem again using the available tools step by step.
                    Break down the problem and use tools for each calculation."""
                )
                messages.append(reminder_message)
                continue
            else:
                # AI is done with calculations
                print("✅ Problem solved! No more tools needed.")
                
                # Analyze solution quality
                print(f"\n📈 Solution Analysis:")
                print(f"   - Tools used: {len(tool_usage_history)}")
                print(f"   - Iterations: {iteration}")
                print(f"   - Tool pattern: {', '.join(set(tool_usage_history))}")
                break
    
    if iteration >= max_iterations:
        print("⚠️  Reached maximum iterations - stopping to prevent infinite loop")
        print("💡 This might indicate the problem needs rephrasing or the solution approach needs adjustment")
    
    # Provide enhanced summary
    print(f"\n🎯 Final Response Quality Metrics:")
    print(f"   - Problem complexity handled: {'High' if iteration > 3 else 'Medium' if iteration > 1 else 'Low'}")
    print(f"   - Tool efficiency: {len(set(tool_usage_history))} unique tools used")
    print(f"   - Error recovery: {'Yes' if any('Error' in str(msg.content) for msg in messages if hasattr(msg, 'content')) else 'No'}")
    
    if langfuse_handler:
        print("\n📊 Check your Langfuse dashboard for detailed traces!")
        print("   - See token usage and costs")
        print("   - Analyze tool usage patterns") 
        print("   - Debug any issues that occurred")
        print("   - Compare different prompting strategies")
    
    return response.content
