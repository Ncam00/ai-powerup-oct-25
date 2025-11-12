"""
Prompting Strategy Comparison Tool
Compare different prompting approaches to see the improvements
"""

from calculator_agent import solve_math_problem, create_calculator_agent
from langchain_core.messages import HumanMessage
import time


def basic_prompt_test(problem: str):
    """Test with the old basic prompting approach"""
    print("📝 BASIC PROMPT APPROACH")
    print("-" * 30)
    
    agent = create_calculator_agent()
    
    # Old basic prompt
    basic_prompt = f"""
Solve this math problem: {problem}

You have calculator tools available. Use them to perform calculations step by step.
Show your work and explain each step clearly.
Always use the calculator tools rather than doing mental math.
"""
    
    messages = [HumanMessage(content=basic_prompt)]
    response = agent.invoke(messages)
    
    print(f"🤖 Basic Response: {response.content}")
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🛠️ Tools called: {len(response.tool_calls)}")
        for tool_call in response.tool_calls:
            print(f"   - {tool_call['name']}({tool_call['args']})")
    else:
        print("⚠️ No tools were called!")
    
    return response


def enhanced_prompt_test(problem: str):
    """Test with the new enhanced prompting approach"""
    print("🧠 ENHANCED PROMPT APPROACH")
    print("-" * 30)
    
    # This will use our enhanced prompting system
    result = solve_math_problem(problem)
    return result


def compare_prompting_strategies():
    """Compare basic vs enhanced prompting on the same problems"""
    
    print("🔬 PROMPTING STRATEGY COMPARISON")
    print("=" * 60)
    print("This tool compares basic vs enhanced prompting approaches")
    print("=" * 60)
    
    test_problems = [
        "What is 15 + 27?",
        "Calculate the square root of 144",
        "What is 2 to the power of 8?",
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n📊 COMPARISON TEST {i}")
        print(f"Problem: {problem}")
        print("=" * 50)
        
        # Test basic approach
        print("\\n1️⃣ BASIC PROMPTING:")
        start_time = time.time()
        try:
            basic_result = basic_prompt_test(problem)
            basic_time = time.time() - start_time
            basic_success = True
        except Exception as e:
            basic_time = time.time() - start_time
            basic_success = False
            print(f"❌ Basic approach failed: {e}")
        
        print("\\n" + "─" * 50)
        
        # Test enhanced approach  
        print("\\n2️⃣ ENHANCED PROMPTING:")
        start_time = time.time()
        try:
            enhanced_result = enhanced_prompt_test(problem)
            enhanced_time = time.time() - start_time
            enhanced_success = True
        except Exception as e:
            enhanced_time = time.time() - start_time
            enhanced_success = False
            print(f"❌ Enhanced approach failed: {e}")
        
        # Compare results
        print("\\n📈 COMPARISON SUMMARY:")
        print("─" * 30)
        print(f"Basic Prompting:    {'✅ Success' if basic_success else '❌ Failed'} ({basic_time:.2f}s)")
        print(f"Enhanced Prompting: {'✅ Success' if enhanced_success else '❌ Failed'} ({enhanced_time:.2f}s)")
        
        if basic_success and enhanced_success:
            print("🎯 Both approaches succeeded - check quality differences above")
        elif enhanced_success and not basic_success:
            print("🏆 Enhanced prompting fixed a failure case!")
        elif not enhanced_success and basic_success:
            print("⚠️ Enhanced prompting introduced an issue - needs investigation")
        else:
            print("🔧 Both approaches failed - problem may need different handling")
        
        print("\\n" + "=" * 70)


def analyze_prompting_improvements():
    """Analyze specific improvements made in enhanced prompting"""
    
    print("\\n\\n🔍 PROMPTING IMPROVEMENT ANALYSIS")
    print("=" * 50)
    
    improvements = {
        "🎯 Role-Based Prompting": {
            "Before": "Generic 'solve this problem' instruction",
            "After": "Specific 'EXPERT MATHEMATICAL ASSISTANT' persona with clear mission",
            "Benefit": "AI understands its role and responsibilities better"
        },
        
        "🧠 Chain-of-Thought": {
            "Before": "Basic 'show your work' instruction", 
            "After": "5-step analysis framework with explicit reasoning stages",
            "Benefit": "More structured and thorough problem solving approach"
        },
        
        "🛠️ Tool Usage Enforcement": {
            "Before": "Suggestion to use tools",
            "After": "Explicit rules with NEVER/ALWAYS statements and detailed tool descriptions", 
            "Benefit": "Eliminates mental math, ensures tool usage"
        },
        
        "📋 Response Format": {
            "Before": "Unstructured output",
            "After": "5-section format: Understanding → Strategy → Calculations → Answer → Verification",
            "Benefit": "Consistent, educational, and clear presentation"
        },
        
        "🚨 Error Handling": {
            "Before": "Basic error messages",
            "After": "Detailed troubleshooting guidance with specific suggestions",
            "Benefit": "AI can recover from errors and learn from mistakes"
        },
        
        "🔄 Pattern Detection": {
            "Before": "No loop detection",
            "After": "Repeated call detection with automatic intervention",
            "Benefit": "Prevents infinite loops and improves efficiency"
        }
    }
    
    for improvement, details in improvements.items():
        print(f"\\n{improvement}")
        print("─" * 40)
        print(f"Before: {details['Before']}")
        print(f"After:  {details['After']}")
        print(f"💡 Benefit: {details['Benefit']}")


if __name__ == "__main__":
    print("🚀 Starting prompting strategy comparison...\\n")
    
    # Run comparison tests
    compare_prompting_strategies()
    
    # Analyze improvements
    analyze_prompting_improvements()
    
    print("\\n🎓 CONCLUSION:")
    print("Enhanced prompting provides:")
    print("✅ More reliable tool usage")
    print("✅ Better structured responses") 
    print("✅ Improved error handling")
    print("✅ Clearer reasoning process")
    print("✅ Prevention of common failure modes")
    print("\\n💡 Try running both test files to see the improvements in action!")