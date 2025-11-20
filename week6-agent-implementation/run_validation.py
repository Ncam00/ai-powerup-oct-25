"""
Simple Test Runner (No pytest required)
========================================

Runs basic validation tests for the agent implementation.
"""

import sys
import asyncio
from agent import create_agent_executor

async def test_calculator():
    """Test calculator tool"""
    print("🧪 Testing Calculator Tool...")
    agent = create_agent_executor()
    
    result = await agent.ainvoke({
        "messages": [("user", "What is 25 * 4?")],
        "iterations": 0
    })
    
    final_msg = result["messages"][-1].content
    if "100" in final_msg:
        print("  ✅ Calculator test passed")
        return True
    else:
        print(f"  ❌ Calculator test failed: {final_msg}")
        return False

async def test_time():
    """Test time tool"""
    print("🧪 Testing Time Tool...")
    agent = create_agent_executor()
    
    result = await agent.ainvoke({
        "messages": [("user", "What time is it in UTC?")],
        "iterations": 0
    })
    
    final_msg = result["messages"][-1].content
    if any(word in final_msg.lower() for word in ["time", "utc", ":"]):
        print("  ✅ Time test passed")
        return True
    else:
        print(f"  ❌ Time test failed: {final_msg}")
        return False

async def test_search():
    """Test search tool"""
    print("🧪 Testing Search Tool...")
    agent = create_agent_executor()
    
    result = await agent.ainvoke({
        "messages": [("user", "Search for information about Python programming")],
        "iterations": 0
    })
    
    final_msg = result["messages"][-1].content
    if "python" in final_msg.lower():
        print("  ✅ Search test passed")
        return True
    else:
        print(f"  ❌ Search test failed: {final_msg}")
        return False

async def test_multi_step():
    """Test multi-step reasoning"""
    print("🧪 Testing Multi-Step Reasoning...")
    agent = create_agent_executor()
    
    result = await agent.ainvoke({
        "messages": [("user", "Calculate 10 + 5, then multiply by 2")],
        "iterations": 0
    })
    
    final_msg = result["messages"][-1].content
    if "30" in final_msg:
        print("  ✅ Multi-step test passed")
        return True
    else:
        print(f"  ❌ Multi-step test failed: {final_msg}")
        return False

async def test_iteration_limit():
    """Test iteration limit enforcement"""
    print("🧪 Testing Iteration Limit...")
    agent = create_agent_executor()
    
    result = await agent.ainvoke({
        "messages": [("user", "Keep calculating random numbers forever")],
        "iterations": 0
    })
    
    iterations = result.get("iterations", 0)
    if iterations <= 10:
        print(f"  ✅ Iteration limit test passed (stopped at {iterations})")
        return True
    else:
        print(f"  ❌ Iteration limit test failed: {iterations} iterations")
        return False

async def main():
    """Run all tests"""
    print("="*70)
    print("AGENT VALIDATION TEST SUITE")
    print("="*70)
    print()
    
    # Check for OpenAI API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   Tests will fail without API key")
        print()
    
    tests = [
        test_calculator,
        test_time,
        test_search,
        test_multi_step,
        test_iteration_limit
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
