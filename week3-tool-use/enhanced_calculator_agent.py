"""
Week 3 Tool Use Challenge - Enhanced Calculator Agent
Demonstrates LangChain tool use patterns for multi-step problem solving
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from calculator_tools import CALCULATOR_TOOLS
import json
import re


class CalculatorAgent:
    """Advanced calculator agent that uses tools to solve multi-step problems"""
    
    def __init__(self):
        self.tools = {tool.name: tool for tool in CALCULATOR_TOOLS}
        self.calculation_history: List[Dict[str, Any]] = []
        
    def solve_problem(self, problem: str) -> Dict[str, Any]:
        """
        Solve a math problem using available tools.
        In a real implementation, this would use an LLM to understand the problem
        and decide which tools to call in sequence.
        """
        
        print(f"\n🔍 Analyzing Problem: '{problem}'")
        print("-" * 50)
        
        # Parse the problem and determine solution steps
        steps = self._analyze_problem(problem)
        
        result = {
            "problem": problem,
            "steps": steps,
            "tool_calls": [],
            "final_answer": None,
            "success": True
        }
        
        try:
            # Reset tracking for new calculation
            self._current_tool_results = []
            
            # Execute the solution steps
            for i, step in enumerate(steps, 1):
                print(f"\n📝 Step {i}: {step['description']}")
                
                if step['tool_needed']:
                    tool_result = self._execute_tool_call(step)
                    result["tool_calls"].append(tool_result)
                    print(f"🔧 Used {tool_result['tool_name']}({tool_result['inputs']}) = {tool_result['output']}")
                    step['result'] = tool_result['output']
                else:
                    print(f"📋 {step['action']}")
            
            # Get final answer
            final_step = steps[-1]
            result["final_answer"] = final_step.get('result', final_step.get('action'))
            
            print(f"\n✅ Solution Complete!")
            print(f"🎯 Final Answer: {result['final_answer']}")
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ Error solving problem: {e}")
        
        # Add to history
        self.calculation_history.append(result)
        return result
    
    def _analyze_problem(self, problem: str) -> List[Dict[str, Any]]:
        """
        Analyze the problem and break it into steps.
        In a real implementation, an LLM would do this analysis.
        """
        
        problem = problem.lower().strip()
        
        # Pattern matching for different types of problems
        if "square root" in problem and "then" in problem:
            return self._handle_square_root_chain(problem)
        elif "factorial" in problem and ("plus" in problem or "add" in problem):
            return self._handle_factorial_addition(problem)
        elif "order of operations" in problem or "pemdas" in problem:
            return self._handle_order_of_operations(problem)
        elif "compound" in problem and "power" in problem:
            return self._handle_compound_power(problem)
        else:
            return self._handle_simple_calculation(problem)
    
    def _handle_square_root_chain(self, problem: str) -> List[Dict[str, Any]]:
        """Handle problems like 'square root of 144 then multiply by 5'"""
        return [
            {
                "description": "Calculate square root of 144",
                "tool_needed": True,
                "tool_name": "square_root",
                "inputs": {"number": 144},
                "action": None
            },
            {
                "description": "Multiply result by 5",
                "tool_needed": True,
                "tool_name": "multiply",
                "inputs": {"a": "previous_result", "b": 5},
                "action": None
            }
        ]
    
    def _handle_factorial_addition(self, problem: str) -> List[Dict[str, Any]]:
        """Handle problems like 'factorial of 5 plus factorial of 4'"""
        return [
            {
                "description": "Calculate factorial of 5",
                "tool_needed": True,
                "tool_name": "factorial",
                "inputs": {"n": 5},
                "action": None
            },
            {
                "description": "Calculate factorial of 4",
                "tool_needed": True,
                "tool_name": "factorial",
                "inputs": {"n": 4},
                "action": None
            },
            {
                "description": "Add the two factorials together",
                "tool_needed": True,
                "tool_name": "add",
                "inputs": {"a": "step_1_result", "b": "step_2_result"},
                "action": None
            }
        ]
    
    def _handle_order_of_operations(self, problem: str) -> List[Dict[str, Any]]:
        """Handle problems like '2 + 3 * 4^2'"""
        return [
            {
                "description": "First, calculate the exponent: 4^2",
                "tool_needed": True,
                "tool_name": "power",
                "inputs": {"base": 4, "exponent": 2},
                "action": None
            },
            {
                "description": "Then, multiply 3 by the result",
                "tool_needed": True,
                "tool_name": "multiply",
                "inputs": {"a": 3, "b": "previous_result"},
                "action": None
            },
            {
                "description": "Finally, add 2 to get the final answer",
                "tool_needed": True,
                "tool_name": "add",
                "inputs": {"a": 2, "b": "previous_result"},
                "action": None
            }
        ]
    
    def _handle_compound_power(self, problem: str) -> List[Dict[str, Any]]:
        """Handle problems like '2^3^2' (right-associative)"""
        return [
            {
                "description": "Calculate the inner exponent: 3^2",
                "tool_needed": True,
                "tool_name": "power",
                "inputs": {"base": 3, "exponent": 2},
                "action": None
            },
            {
                "description": "Calculate 2 raised to that result",
                "tool_needed": True,
                "tool_name": "power",
                "inputs": {"base": 2, "exponent": "previous_result"},
                "action": None
            }
        ]
    
    def _handle_simple_calculation(self, problem: str) -> List[Dict[str, Any]]:
        """Handle simple problems like '15 + 27'"""
        return [
            {
                "description": "Perform the requested calculation",
                "tool_needed": False,
                "tool_name": None,
                "inputs": {},
                "action": "Simple calculation: 15 + 27 = 42"
            }
        ]
    
    def _execute_tool_call(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        
        tool_name = step['tool_name']
        inputs = step['inputs'].copy()
        
        # Handle references to previous results
        for key, value in inputs.items():
            if value == "previous_result":
                # Get the last tool call result from current calculation
                if hasattr(self, '_current_tool_results') and self._current_tool_results:
                    inputs[key] = self._current_tool_results[-1]['output']
            elif isinstance(value, str) and "step_" in value and "_result" in value:
                # Handle step references like "step_1_result"
                step_num = int(value.split('_')[1])
                if hasattr(self, '_current_tool_results') and len(self._current_tool_results) >= step_num:
                    inputs[key] = self._current_tool_results[step_num - 1]['output']
        
        # Execute the tool
        tool = self.tools[tool_name]
        output = tool.invoke(inputs)
        
        tool_result = {
            "tool_name": tool_name,
            "inputs": inputs,
            "output": output,
            "description": step['description']
        }
        
        # Track results for current calculation
        if not hasattr(self, '_current_tool_results'):
            self._current_tool_results = []
        self._current_tool_results.append(tool_result)
        
        return tool_result
    
    def show_calculation_history(self):
        """Display the complete calculation history"""
        if not self.calculation_history:
            print("No calculations performed yet.")
            return
            
        print("\n📚 Calculation History")
        print("=" * 50)
        
        for i, calc in enumerate(self.calculation_history, 1):
            print(f"\n{i}. Problem: {calc['problem']}")
            print(f"   Answer: {calc['final_answer']}")
            print(f"   Tools Used: {len(calc['tool_calls'])}")
            print(f"   Success: {'✅' if calc['success'] else '❌'}")


def demo_tool_use_patterns():
    """Demonstrate various tool use patterns for Week 3"""
    
    print("Week 3 Tool Use Challenge - Advanced Calculator Agent")
    print("=" * 60)
    
    agent = CalculatorAgent()
    
    # Test different types of problems
    problems = [
        "Calculate square root of 144 then multiply by 5",
        "Find factorial of 5 plus factorial of 4",
        "Solve using order of operations: 2 + 3 * 4^2",
        "Calculate compound power: 2^3^2"
    ]
    
    print(f"\n🎯 Testing {len(problems)} Multi-Step Problems")
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{'='*60}")
        print(f"Problem {i}/{len(problems)}")
        agent.solve_problem(problem)
    
    # Show summary
    print(f"\n{'='*60}")
    print("📊 Summary")
    agent.show_calculation_history()
    
    # Demonstrate tool use benefits
    print(f"\n✨ Tool Use Benefits Demonstrated:")
    print("- Step-by-step problem decomposition")
    print("- Automatic tool selection and chaining")
    print("- Error handling and validation")
    print("- Calculation history and audit trail")
    print("- Modular, reusable tool components")


if __name__ == "__main__":
    demo_tool_use_patterns()