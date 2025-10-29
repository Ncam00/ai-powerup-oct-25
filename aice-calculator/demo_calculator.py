"""
Simple calculator agent demo without external dependencies
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from calculator_tools import CALCULATOR_TOOLS

load_dotenv()

def solve_math_problem_demo(problem: str):
    """Solve a math problem using AI agent with tools - simplified demo version"""
    
    print(f"🤖 Solving: {problem}")
    print("=" * 50)
    
    # Initialize the LLM with tools
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(CALCULATOR_TOOLS)
    
    # Create the initial message
    messages = [
        HumanMessage(content=f"""
        Please solve this math problem step by step: {problem}
        
        Use the available tools to perform calculations. 
        Show your work and explain each step clearly.
        """)
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Step {iteration}:")
        
        # Get response from LLM
        response = llm_with_tools.invoke(messages)
        print(f"💭 AI thinks: {response.content}")
        
        # Add AI response to messages
        messages.append(response)
        
        # Check if tools were called
        if response.tool_calls:
            print(f"🛠️  Using {len(response.tool_calls)} tool(s):")
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"   📊 {tool_name}({tool_args})")
                
                # Find and execute the tool
                for tool in CALCULATOR_TOOLS:
                    if tool.name == tool_name:
                        try:
                            result = tool.func(**tool_args)
                            print(f"   ✅ Result: {result}")
                            
                            # Add tool result to messages
                            messages.append(ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call["id"]
                            ))
                        except Exception as e:
                            error_msg = f"Error: {str(e)}"
                            print(f"   ❌ {error_msg}")
                            messages.append(ToolMessage(
                                content=error_msg,
                                tool_call_id=tool_call["id"]
                            ))
                        break
        else:
            # No more tools needed, we have the final answer
            print(f"\n🎯 Final Answer: {response.content}")
            break
    
    print("\n" + "=" * 50)
    return response.content

if __name__ == "__main__":
    # Test problems
    problems = [
        "What is the square root of 144 plus 10?",
        "Calculate 25 factorial divided by 20 factorial",
        "What is 2^8 + 3^4?",
    ]
    
    for problem in problems:
        solve_math_problem_demo(problem)
        print("\n" + "🔄" * 20 + "\n")