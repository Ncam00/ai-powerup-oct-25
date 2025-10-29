"""
Enhanced PythonMentor AI - Week 3 Version
Incorporates Structured Output, Custom Tools, and Observability
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks.base import BaseCallbackHandler
from learning_models import ConversationAnalysis, StudentProgress, SkillLevel, LearningObjective
from learning_tools import PYTHON_LEARNING_TOOLS
import uuid
from datetime import datetime

# Try to import Langfuse, but gracefully handle if not available
try:
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    CallbackHandler = None

# Load environment variables
load_dotenv()

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses to Streamlit"""
    
    def __init__(self, container):
        self.container = container
        self.text = ""
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.text += token
        self.container.markdown(self.text + "▌")

def get_langfuse_handler():
    """Create Langfuse callback handler for learning analytics"""
    if not LANGFUSE_AVAILABLE:
        return None
        
    try:
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        
        if secret_key and public_key and not secret_key.endswith("..."):
            return CallbackHandler(
                secret_key=secret_key,
                public_key=public_key,
                host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com"),
                session_id=st.session_state.get("session_id", str(uuid.uuid4())),
                user_id=st.session_state.get("student_id", "demo_student")
            )
        return None
    except Exception:
        return None

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if "student_level" not in st.session_state:
        st.session_state.student_level = "beginner"
    if "topics_covered" not in st.session_state:
        st.session_state.topics_covered = set()
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "student_id" not in st.session_state:
        st.session_state.student_id = "demo_student"
    if "student_progress" not in st.session_state:
        # Initialize with structured progress tracking
        st.session_state.student_progress = StudentProgress(
            student_id=st.session_state.student_id,
            current_level=SkillLevel(st.session_state.student_level)
        )
    if "enable_tools" not in st.session_state:
        st.session_state.enable_tools = True
    if "enable_observability" not in st.session_state:
        st.session_state.enable_observability = True

def get_enhanced_tutor_system_prompt(level: str, enable_tools: bool) -> str:
    """Create enhanced system prompt for Python tutor with Week 3 capabilities"""
    base_prompt = """You are PythonMentor AI, an enhanced expert Python programming tutor with advanced capabilities:

**Core Teaching Philosophy:**
1. **Socratic Method**: Ask guiding questions to help students discover answers
2. **Learn by Doing**: Provide hands-on examples and coding exercises  
3. **Tool-Assisted Learning**: Use available tools to demonstrate concepts
4. **Structured Progress**: Track and analyze learning progress systematically
5. **Mistake-Friendly**: Encourage experimentation and learning from errors

**Enhanced Capabilities (Week 3):**
- Execute Python code safely to demonstrate concepts
- Validate student code before execution
- Provide detailed error explanations
- Generate personalized coding exercises
- Track learning progress with structured data
"""

    if enable_tools:
        tools_prompt = """
**Available Tools:**
- execute_python_code: Run Python code and show output
- validate_python_syntax: Check code syntax before execution
- explain_python_error: Provide beginner-friendly error explanations
- suggest_learning_topics: Recommend next topics based on progress
- create_coding_exercise: Generate practice exercises

**Tool Usage Guidelines:**
- Use execute_python_code to demonstrate concepts with real examples
- Always validate syntax before executing student code
- When students encounter errors, use explain_python_error for clear explanations
- Suggest appropriate exercises using create_coding_exercise
- Use suggest_learning_topics to provide personalized learning paths
"""
    else:
        tools_prompt = "**Tools are currently disabled** - focus on explanations and guidance without code execution."

    level_prompts = {
        "beginner": """
**Student Level: Complete Beginner**
- Assume no prior programming experience
- Use tools to show simple, clear examples
- Start with basic concepts like variables and print statements
- Execute code frequently to show immediate results
- Be very patient and encouraging
""",
        "intermediate": """
**Student Level: Some Programming Experience**
- Student knows basics but needs practice with advanced concepts
- Use tools to demonstrate more complex examples
- Show debugging techniques and error handling
- Encourage experimentation with different approaches
""",
        "advanced": """
**Student Level: Experienced Programmer**  
- Focus on best practices and optimization
- Use tools to demonstrate advanced concepts and performance
- Provide challenging problems and code review
- Explore Python's advanced features and ecosystem
"""
    }

    return base_prompt + tools_prompt + level_prompts.get(level, level_prompts["beginner"])

def setup_enhanced_llm(api_key: str, student_level: str, enable_tools: bool = True):
    """Set up enhanced LLM with tools and observability"""
    if not api_key:
        st.error("Please provide an OpenAI API key!")
        st.stop()
    
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4",
        temperature=0.7,
        streaming=True
    )
    
    # Bind tools if enabled
    if enable_tools:
        llm_with_tools = llm.bind_tools(PYTHON_LEARNING_TOOLS)
        return llm_with_tools
    else:
        return llm

def analyze_conversation_with_ai(conversation_messages, llm):
    """Use AI to analyze the conversation and extract structured learning data"""
    analysis_prompt = """
    Analyze this tutoring conversation and extract learning information in the following format:
    
    Topics Discussed: [list of Python topics/concepts discussed]
    Student Questions: [questions asked by the student]
    Code Examples: [any code examples shown or discussed]
    Learning Objectives: [learning objectives that were addressed]
    Understanding Level: [estimate 0.0-1.0 how well student understood]
    Next Topics: [suggested topics for next session]
    Session Summary: [brief summary of what was learned]
    
    Focus on Python programming concepts and learning progress.
    """
    
    try:
        analysis_messages = conversation_messages[-6:] + [HumanMessage(content=analysis_prompt)]
        response = llm.invoke(analysis_messages)
        
        # Parse the response into structured data (simplified parsing)
        content = response.content
        
        # Extract topics (this is a simple implementation - could be enhanced)
        topics = []
        if "Topics Discussed:" in content:
            topics_line = content.split("Topics Discussed:")[1].split("\\n")[0]
            topics = [t.strip() for t in topics_line.split(",") if t.strip()]
        
        return ConversationAnalysis(
            topics_discussed=topics,
            session_summary=content[:200] + "..." if len(content) > 200 else content,
            student_understanding_level=0.8  # Default estimate
        )
    except Exception:
        return ConversationAnalysis(
            topics_discussed=["General discussion"],
            session_summary="Learning session completed"
        )

def main():
    """Enhanced main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="PythonMentor AI - Enhanced",
        page_icon="🐍",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🐍 PythonMentor AI - Enhanced Edition")
    st.markdown("*Your Personal Python Programming Tutor with Advanced Week 3 Features*")
    
    # Feature highlights
    with st.expander("✨ New Week 3 Features", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎯 Structured Output**\\n- Detailed progress tracking\\n- Learning objective analysis\\n- Structured conversation insights")
        with col2:
            st.markdown("**🛠️ Custom Tools**\\n- Execute Python code safely\\n- Validate syntax\\n- Generate exercises")
        with col3:
            st.markdown("**📊 Observability**\\n- Learning analytics\\n- Session tracking\\n- Performance monitoring")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🎓 Enhanced Learning Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_api_key,
            help="Enter your OpenAI API key to start learning"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
        
        st.markdown("---")
        
        # Enhanced features toggles
        st.subheader("🚀 Week 3 Features")
        
        st.session_state.enable_tools = st.checkbox(
            "Enable Learning Tools",
            value=st.session_state.enable_tools,
            help="Allows code execution, syntax validation, and exercise generation"
        )
        
        st.session_state.enable_observability = st.checkbox(
            "Enable Learning Analytics",
            value=st.session_state.enable_observability,
            help="Track learning progress with Langfuse observability"
        )
        
        # Student level selection
        st.session_state.student_level = st.selectbox(
            "Your Programming Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.student_level),
            help="This helps the tutor adjust explanations to your level"
        )
        
        st.markdown("---")
        
        # Enhanced learning progress with structured data
        st.subheader("📚 Structured Learning Progress")
        
        progress = st.session_state.student_progress
        
        # Update progress level if changed
        if progress.current_level.value != st.session_state.student_level:
            progress.current_level = SkillLevel(st.session_state.student_level)
        
        # Display progress metrics
        st.metric("Total Sessions", progress.total_sessions)
        st.metric("Topics Covered", len(st.session_state.topics_covered))
        
        if st.session_state.topics_covered:
            st.write("**Recent Topics:**")
            for topic in sorted(list(st.session_state.topics_covered)[-5:]):
                st.write(f"✅ {topic}")
        else:
            st.write("*No topics covered yet - start chatting!*")
        
        if st.button("Reset All Progress"):
            st.session_state.messages = []
            st.session_state.topics_covered = set()
            st.session_state.student_progress = StudentProgress(
                student_id=st.session_state.student_id,
                current_level=SkillLevel(st.session_state.student_level)
            )
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        
        st.markdown("---")
        
        # Enhanced learning suggestions
        st.subheader("💡 AI-Powered Suggestions")
        if st.button("Get Personalized Learning Path"):
            if st.session_state.enable_tools:
                st.info("Check the main chat - I'll suggest topics based on your progress!")
                # This will be handled in the main chat when tools are enabled
            else:
                st.info("Enable Learning Tools to get AI-powered suggestions!")
    
    # Main chat interface
    if not st.session_state.openai_api_key:
        st.warning("🔑 Please enter your OpenAI API key in the sidebar to start learning!")
        return
    
    # Display enhanced features status
    if st.session_state.enable_tools or st.session_state.enable_observability:
        status_cols = st.columns(3)
        with status_cols[0]:
            if st.session_state.enable_tools:
                st.success("🛠️ Tools Enabled")
            else:
                st.info("🛠️ Tools Disabled")
        with status_cols[1]:
            if st.session_state.enable_observability:
                if get_langfuse_handler():
                    st.success("📊 Analytics Enabled")
                else:
                    st.warning("📊 Analytics: Keys Missing")
            else:
                st.info("📊 Analytics Disabled")
        with status_cols[2]:
            st.info(f"🎓 Level: {st.session_state.student_level.title()}")
    
    # Display chat history
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Python programming..."):
        # Add user message to chat history
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response with enhanced features
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Set up enhanced LLM
                llm = setup_enhanced_llm(
                    st.session_state.openai_api_key, 
                    st.session_state.student_level,
                    st.session_state.enable_tools
                )
                
                # Set up observability
                callbacks = []
                if st.session_state.enable_observability:
                    langfuse_handler = get_langfuse_handler()
                    if langfuse_handler:
                        callbacks.append(langfuse_handler)
                
                # Create enhanced system message
                system_message = SystemMessage(content=get_enhanced_tutor_system_prompt(
                    st.session_state.student_level,
                    st.session_state.enable_tools
                ))
                
                # Prepare conversation
                conversation_messages = [system_message] + st.session_state.messages[-10:]
                
                # Get response with observability
                response = ""
                full_response = llm.invoke(
                    conversation_messages,
                    config={
                        "callbacks": callbacks,
                        "run_name": f"python_tutoring_session",
                        "metadata": {
                            "student_level": st.session_state.student_level,
                            "tools_enabled": st.session_state.enable_tools,
                            "session_id": st.session_state.session_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )
                
                response = full_response.content
                message_placeholder.markdown(response)
                
                # Add AI response to chat history
                ai_message = AIMessage(content=response)
                st.session_state.messages.append(ai_message)
                
                # Enhanced topic tracking
                python_topics = [
                    "variables", "functions", "lists", "dictionaries", "loops", "conditionals",
                    "classes", "objects", "exceptions", "files", "strings", "tuples", "sets",
                    "comprehensions", "decorators", "generators", "modules"
                ]
                
                for topic in python_topics:
                    if topic in prompt.lower() or topic in response.lower():
                        st.session_state.topics_covered.add(topic.title())
                
                # Update session count
                st.session_state.student_progress.total_sessions += 1
                
                # Show analytics info if enabled
                if st.session_state.enable_observability and callbacks:
                    st.info("📊 This conversation is being tracked for learning analytics!")
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()