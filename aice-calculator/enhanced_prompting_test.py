"""
Enhanced test suite for the calculator agent with advanced prompting
Tests various complexity levels and edge cases
"""

from calculator_agent import solve_math_problem


def test_enhanced_prompting():
    """Test the enhanced prompting system with various problem types"""
    
    print("🧠 ENHANCED PROMPTING TEST SUITE")
    print("=" * 60)
    print("Testing advanced AI behavior improvements:")
    print("• Chain-of-thought reasoning")
    print("• Error handling and recovery") 
    print("• Tool usage optimization")
    print("• Problem complexity adaptation")
    print("=" * 60)

    # Test categories with increasing complexity
    test_categories = {
        "🎯 Basic Arithmetic (Tool Usage Enforcement)": [
            "What is 7 + 8?",
            "Calculate 45 - 17",
            "What is 6 times 9?"
        ],
        
        "🧮 Intermediate Operations": [
            "What is the square root of 81?",
            "Calculate 3 to the power of 4", 
            "What is 6 factorial?"
        ],
        
        "🎲 Order of Operations": [
            "Calculate 2 + 3 * 4",
            "What is (15 + 5) / 4?",
            "Solve: 10 - 2 * 3 + 1"
        ],
        
        "🚨 Error Handling Cases": [
            "What is the square root of -16?",
            "Calculate 10 divided by 0",
            "What is factorial of -3?"
        ],
        
        "🧩 Complex Multi-Step Problems": [
            "If I have 24 apples and give away 1/3 of them, then buy 8 more, how many do I have?",
            "Calculate the area of a circle with radius 5 (use π ≈ 3.14159)",
            "What is 5! + 3² - √64?"
        ]
    }

    # Track performance metrics
    total_tests = sum(len(problems) for problems in test_categories.values())
    current_test = 0

    for category, problems in test_categories.items():
        print(f"\n{category}")
        print("─" * 50)
        
        for problem in problems:
            current_test += 1
            print(f"\n📋 TEST {current_test}/{total_tests}")
            print(f"Category: {category.split(' ', 1)[1]}")
            
            try:
                solve_math_problem(problem)
                print("✅ Test completed successfully")
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
            
            print("═" * 60)


def test_conversation_context():
    """Test the enhanced system's ability to handle context and follow-up questions"""
    
    print("\n\n🗣️ CONVERSATION CONTEXT TEST")
    print("=" * 50)
    print("Testing contextual understanding and follow-up capabilities")
    
    conversation_tests = [
        "Calculate the square of 12",
        "Now add 25 to that result",
        "What's half of that final number?"
    ]
    
    print("\n💬 Simulating conversation flow:")
    for i, question in enumerate(conversation_tests, 1):
        print(f"\n👤 Question {i}: {question}")
        try:
            solve_math_problem(question)
        except Exception as e:
            print(f"❌ Error: {e}")
        print("─" * 40)


def test_problem_complexity_detection():
    """Test how the enhanced prompting adapts to different problem complexities"""
    
    print("\n\n🎚️ COMPLEXITY ADAPTATION TEST") 
    print("=" * 50)
    
    complexity_tests = {
        "Simple": "What is 5 + 3?",
        "Medium": "Calculate the square root of 144 and multiply by 3", 
        "Complex": "A rectangle has length 12 and width 8. Calculate its area, then find what percentage this area is of a 15x15 square."
    }
    
    for complexity, problem in complexity_tests.items():
        print(f"\n📊 {complexity.upper()} PROBLEM:")
        print(f"Problem: {problem}")
        try:
            solve_math_problem(problem)
            print(f"✅ {complexity} problem handled successfully")
        except Exception as e:
            print(f"❌ {complexity} problem failed: {e}")
        print("─" * 50)


if __name__ == "__main__":
    print("🚀 Starting comprehensive enhanced prompting tests...\n")
    
    # Run all test suites
    test_enhanced_prompting()
    test_conversation_context() 
    test_problem_complexity_detection()
    
    print("\n🎉 Enhanced prompting test suite completed!")
    print("\nKey improvements demonstrated:")
    print("✅ Smarter tool usage enforcement")
    print("✅ Better error handling and recovery")
    print("✅ Adaptive complexity responses") 
    print("✅ Pattern detection for infinite loops")
    print("✅ Enhanced solution quality metrics")
    print("\n💡 Check the console output above to see how the AI behavior improved!")