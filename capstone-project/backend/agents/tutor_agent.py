"""
Multi-Agent Tutoring System
============================

Week 6: Autonomous agents with LangGraph
Integrates tutor, code reviewer, and quiz generator agents
"""

from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import logging

from tools.code_executor import execute_python_code
from tools.concept_search import search_concepts
from tools.code_analyzer import analyze_code_quality
from api.models.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITION
# ============================================================================

class TutorState(TypedDict):
    """State for tutoring agent system"""
    messages: Annotated[list, operator.add]
    student_code: str | None
    current_topic: str | None
    difficulty_level: str
    needs_code_review: bool
    needs_quiz: bool
    needs_concept_help: bool
    iteration_count: int
    session_id: str

# ============================================================================
# SPECIALIZED AGENTS
# ============================================================================

class TutorAgent:
    """Main teaching orchestrator agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.AGENT_TEMPERATURE
        )
    
    def create_system_prompt(self, difficulty: str) -> str:
        """Create educational prompt based on difficulty"""
        base_prompt = """You are PythonMentor, an expert Python programming tutor.
        
Your teaching philosophy:
- Use the Socratic method - ask questions to guide learning
- Provide hints before solutions
- Celebrate progress and encourage growth mindset
- Adapt explanations to student's level
- Use analogies and real-world examples
- Break complex topics into manageable pieces

Your capabilities:
- Explain Python concepts with examples
- Review and provide feedback on student code
- Generate practice exercises
- Search Python documentation
- Execute code to demonstrate concepts

Current student level: {difficulty}"""
        
        difficulty_guidance = {
            "beginner": "\n\nFor beginners: Use simple language, avoid jargon, provide more examples, be very patient.",
            "intermediate": "\n\nFor intermediate: Can use some technical terms, focus on best practices, challenge them slightly.",
            "advanced": "\n\nFor advanced: Use precise terminology, discuss trade-offs, focus on optimization and design patterns."
        }
        
        return base_prompt.format(difficulty=difficulty.upper()) + difficulty_guidance.get(difficulty, "")
    
    async def teach(self, state: TutorState) -> dict:
        """Main teaching logic"""
        messages = state["messages"]
        system_prompt = self.create_system_prompt(state["difficulty_level"])
        
        # Bind tools to LLM
        tools = [execute_python_code, search_concepts, analyze_code_quality]
        llm_with_tools = self.llm.bind_tools(tools)
        
        # Create full message history
        full_messages = [SystemMessage(content=system_prompt)] + messages
        
        # Get LLM response
        response = await llm_with_tools.ainvoke(full_messages)
        
        logger.info(f"Tutor response: {response.content[:100]}...")
        
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1
        }

class CodeReviewerAgent:
    """Specialized agent for code review"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3  # Lower temperature for more consistent reviews
        )
    
    async def review(self, code: str, difficulty: str) -> dict:
        """Perform detailed code review"""
        
        review_prompt = f"""You are a code reviewer for Python learning.
        
Review this student code (level: {difficulty}):

```python
{code}
```

Provide:
1. What's working well (be specific and encouraging)
2. Issues to fix (prioritize by importance)
3. Best practice suggestions
4. Pythonic improvements
5. Overall score (0-100)

Be constructive and educational. Explain WHY changes are needed."""
        
        response = await self.llm.ainvoke([HumanMessage(content=review_prompt)])
        
        return {
            "review": response.content,
            "timestamp": "now"
        }

class QuizGeneratorAgent:
    """Specialized agent for generating quizzes"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.8  # Higher temperature for variety
        )
    
    async def generate_quiz(self, topic: str, difficulty: str, num_questions: int = 5) -> dict:
        """Generate practice quiz"""
        
        quiz_prompt = f"""Generate a Python quiz on: {topic}
        
Difficulty: {difficulty}
Number of questions: {num_questions}

For each question, provide:
1. Clear question text
2. 4 multiple choice options (label A, B, C, D)
3. Correct answer
4. Explanation of why it's correct

Topics to cover: fundamentals, common patterns, edge cases.

Format as JSON array of questions."""
        
        response = await self.llm.ainvoke([HumanMessage(content=quiz_prompt)])
        
        return {
            "quiz": response.content,
            "topic": topic,
            "difficulty": difficulty
        }

# ============================================================================
# GRAPH NODES
# ============================================================================

async def tutor_node(state: TutorState) -> dict:
    """Main tutoring node"""
    tutor = TutorAgent()
    return await tutor.teach(state)

async def tool_execution_node(state: TutorState) -> dict:
    """Execute tools requested by tutor"""
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
    
    from langchain_core.messages import ToolMessage
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Execute the tool
        if tool_name == "execute_python_code":
            result = execute_python_code.invoke(tool_args)
        elif tool_name == "search_concepts":
            result = search_concepts.invoke(tool_args)
        elif tool_name == "analyze_code_quality":
            result = analyze_code_quality.invoke(tool_args)
        else:
            result = f"Unknown tool: {tool_name}"
        
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )
        tool_messages.append(tool_message)
    
    return {"messages": tool_messages}

async def code_review_node(state: TutorState) -> dict:
    """Dedicated code review"""
    reviewer = CodeReviewerAgent()
    code = state.get("student_code", "")
    
    if not code:
        return {}
    
    review = await reviewer.review(code, state["difficulty_level"])
    
    return {
        "messages": [AIMessage(content=f"Code Review:\n\n{review['review']}")],
        "needs_code_review": False
    }

async def quiz_generation_node(state: TutorState) -> dict:
    """Generate quiz"""
    quiz_gen = QuizGeneratorAgent()
    topic = state.get("current_topic", "Python basics")
    
    quiz = await quiz_gen.generate_quiz(
        topic,
        state["difficulty_level"],
        num_questions=5
    )
    
    return {
        "messages": [AIMessage(content=f"Practice Quiz:\n\n{quiz['quiz']}")],
        "needs_quiz": False
    }

# ============================================================================
# ROUTING LOGIC
# ============================================================================

def should_continue(state: TutorState) -> Literal["tools", "review", "quiz", "end"]:
    """Determine next step"""
    
    # Check iteration limit
    if state.get("iteration_count", 0) >= settings.MAX_AGENT_ITERATIONS:
        return "end"
    
    # Check if code review needed
    if state.get("needs_code_review"):
        return "review"
    
    # Check if quiz needed
    if state.get("needs_quiz"):
        return "quiz"
    
    # Check if last message has tool calls
    messages = state["messages"]
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
    
    return "end"

def should_continue_after_tools(state: TutorState) -> Literal["tutor", "end"]:
    """Continue to tutor after tool execution"""
    if state.get("iteration_count", 0) >= settings.MAX_AGENT_ITERATIONS:
        return "end"
    return "tutor"

# ============================================================================
# BUILD GRAPH
# ============================================================================

def create_tutoring_agent():
    """Create the multi-agent tutoring system"""
    
    workflow = StateGraph(TutorState)
    
    # Add nodes
    workflow.add_node("tutor", tutor_node)
    workflow.add_node("tools", tool_execution_node)
    workflow.add_node("review", code_review_node)
    workflow.add_node("quiz", quiz_generation_node)
    
    # Set entry point
    workflow.set_entry_point("tutor")
    
    # Add conditional routing from tutor
    workflow.add_conditional_edges(
        "tutor",
        should_continue,
        {
            "tools": "tools",
            "review": "review",
            "quiz": "quiz",
            "end": END
        }
    )
    
    # Tools always return to tutor
    workflow.add_conditional_edges(
        "tools",
        should_continue_after_tools,
        {
            "tutor": "tutor",
            "end": END
        }
    )
    
    # Review and quiz return to tutor
    workflow.add_edge("review", "tutor")
    workflow.add_edge("quiz", "tutor")
    
    # Add memory for conversation persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# ============================================================================
# USAGE INTERFACE
# ============================================================================

class TutoringSystem:
    """High-level interface for tutoring system"""
    
    def __init__(self):
        self.agent = create_tutoring_agent()
    
    async def tutor_student(
        self,
        message: str,
        session_id: str,
        difficulty: str = "beginner",
        context: list = None
    ) -> dict:
        """
        Main tutoring interface
        
        Args:
            message: Student's question or code
            session_id: Unique session identifier
            difficulty: beginner/intermediate/advanced
            context: Previous conversation messages
        
        Returns:
            Response with teaching content
        """
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "student_code": None,
            "current_topic": None,
            "difficulty_level": difficulty,
            "needs_code_review": False,
            "needs_quiz": False,
            "needs_concept_help": False,
            "iteration_count": 0,
            "session_id": session_id
        }
        
        # Add conversation history if provided
        if context:
            history_messages = []
            for msg in context:
                if msg["role"] == "user":
                    history_messages.append(HumanMessage(content=msg["content"]))
                else:
                    history_messages.append(AIMessage(content=msg["content"]))
            initial_state["messages"] = history_messages + initial_state["messages"]
        
        # Run the agent
        config = {"configurable": {"thread_id": session_id}}
        
        result = await self.agent.ainvoke(initial_state, config=config)
        
        # Extract final response
        final_message = result["messages"][-1]
        
        return {
            "response": final_message.content,
            "session_id": session_id,
            "iterations": result.get("iteration_count", 0)
        }

# Global instance
tutoring_system = TutoringSystem()
