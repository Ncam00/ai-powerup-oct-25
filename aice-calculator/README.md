# AI Calculator Agent Challenge

Welcome to the AI Calculator Agent challenge! In this project, you'll build an intelligent calculator that can use tools to solve math problems step by step.

## What You'll Build

By the end of this challenge, you'll have created an AI agent that can:
- Take math problems in natural language
- Use calculator tools to perform calculations
- Handle multi-step problems by calling tools iteratively
- Provide clear explanations of its work

## Prerequisites

- Basic Python knowledge
- Understanding of LangChain concepts (tools, agents, messages)
- Google AI API key (get one from [Google AI Studio](https://ai.dev/))

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create a `.env` file with your Google AI API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. Test the existing tools:
   ```bash
   python test_tools.py
   ```

## Phase 1: Understanding the Tools (Guided)

First, let's understand what tools are available. Look at `calculator_tools.py` to see the available functions:

- `add(a, b)` - Adds two numbers
- `subtract(a, b)` - Subtracts second number from first
- `multiply(a, b)` - Multiplies two numbers
- `divide(a, b)` - Divides first number by second
- `power(base, exponent)` - Raises base to the power of exponent
- `square_root(number)` - Calculates square root
- `factorial(n)` - Calculates factorial

**Your Task**: Run `python test_tools.py` to see how these tools work.

## Phase 2: Create the Basic Agent (Step-by-Step Guide)

Now let's implement the `create_calculator_agent()` function in `calculator_agent.py`.

### Step 2.1: Initialize the LLM

Add this code to the `create_calculator_agent()` function:

```python
# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-04-17",
    temperature=0
)
```

### Step 2.2: Bind Tools to the LLM

Add this code right after the LLM initialization:

```python
# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(CALCULATOR_TOOLS)

return llm_with_tools
```

### Step 2.3: Test Your Agent

Now replace the `pass` statement with the code above and test it:

```python
# Test in Python interpreter
from calculator_agent import create_calculator_agent
agent = create_calculator_agent()
print("Agent created successfully!")
```

## Phase 3: Basic Problem Solving (Guided)

Let's implement basic functionality in the `solve_math_problem()` function.

### Step 3.1: Create the Agent and Prompt

Replace the first few TODOs with:

```python
# Create the agent
agent = create_calculator_agent()

# Create a prompt that encourages tool use
prompt = f"""
Solve this math problem: {problem}

Use the available calculator tools to perform calculations.
Show your work and explain each step.
"""

# Send initial message
messages = [HumanMessage(content=prompt)]
response = agent.invoke(messages)

print("AI Response:")
print(response.content)
```

### Step 3.2: Test Basic Functionality

Run `python main.py` to test your basic implementation. You should see the AI responding to math problems.

**Expected behavior**: The AI will try to call tools, but the results won't be sent back yet.

## Phase 4: Handle Tool Calls 

Now let's handle tool calls and send results back to the AI.

### Step 4.1: Check for Tool Calls

Add this code after printing the AI response:

```python
# Check if tools were called
if hasattr(response, 'tool_calls') and response.tool_calls:
    print(f"\\nTools used: {len(response.tool_calls)}")
    
    # Process each tool call
    for i, tool_call in enumerate(response.tool_calls):
        print(f"  {i+1}. {tool_call['name']}: {tool_call['args']}")
        
        # Find the tool function
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        # TODO: Execute the tool and get the result
        # TODO: Create a ToolMessage with the result
        # TODO: Add it to the messages list
```

### Step 4.2: Execute Tools

Here's a hint for executing tools. You need to:

1. Find the correct tool function from `CALCULATOR_TOOLS`
2. Call `tool_function.invoke(tool_args)` to get the result
3. Create a `ToolMessage` with the result and `tool_call_id`
4. Add the message to your messages list

**Your Task**: Implement the tool execution logic. Look at the imports at the top of the file for clues about what you need.

### Step 4.3: Test Tool Execution

Test with simple problems like "What is 15 + 27?" - you should see the tool being called and the result printed.

## Phase 5: Iterative Processing 

The current implementation only calls tools once. For complex problems, we need to send tool results back to the AI and let it make more tool calls if needed.

### Your Challenge

Implement a loop that:

1. Sends messages to the agent
2. Checks for tool calls in the response
3. Executes any tool calls
4. Adds tool results to the message history
5. Repeats until no more tool calls are made

### Hints

- Use a `while` loop
- Add both the AI response AND the tool results to the `messages` list
- The loop should exit when `response.tool_calls` is empty
- Add a maximum iteration limit to prevent infinite loops
- Consider tracking which tools have been called to prevent repeats

### Advanced Challenge

Can you detect when the AI is calling the same tool with the same arguments repeatedly? How would you handle that?

## Phase 6: Testing and Refinement (Independent)

### Test Cases

Your agent should be able to handle:

1. Simple arithmetic: "What is 15 + 27?"
2. Square roots: "Calculate the square root of 144"
3. Order of operations: "What is 23 + 4 / 2 * 3"
4. Factorials: "What is 5 factorial?"
5. Powers: "What is 2 to the power of 8?"

### Your Tasks

1. Test all the problems in `main.py`
2. Add error handling for division by zero
3. Improve the prompt to get better AI behavior
4. Add more test cases

## Success Criteria

Your implementation is successful when:

- ✅ Basic math problems are solved correctly
- ✅ The AI explains its reasoning
- ✅ Tool calls are executed and results are used
- ✅ Complex problems requiring multiple steps work
- ✅ The agent doesn't get stuck in infinite loops
- ✅ Error cases are handled gracefully

## Bonus Challenges

1. **Conversation Memory**: Allow the agent to remember previous calculations in a session
2. **New Tools**: Add tools for trigonometry, logarithms, or other math functions
3. **Better Prompting**: Experiment with different prompts to improve AI behavior
4. **Validation**: Add input validation for the math problems
5. **Web Interface**: Create a simple web interface for the calculator

## Common Issues and Solutions

### Issue: Tools not being called
- Check that `bind_tools()` is called correctly
- Verify your prompt encourages tool use
- Make sure `CALCULATOR_TOOLS` is imported

### Issue: Tool results not being used
- Ensure you're adding `ToolMessage` objects to the messages list
- Check that `tool_call_id` matches the original tool call
- Verify you're sending the updated messages back to the agent

### Issue: Infinite loops
- Add a maximum iteration counter
- Track repeated tool calls
- Improve your prompt to tell the AI when to stop

### Issue: Import errors
- Make sure all dependencies are installed
- Check that your `.env` file contains a valid API key
- Verify file paths and imports

## Need Help?

- Review the test files to understand expected behavior
- Check the original solution branch for reference
- Test individual components before combining them
- Use print statements to debug message flow

Good luck building your AI calculator agent! 🤖🧮
