"""
AI Code Learning Platform - Frontend
=====================================

Streamlit application integrating all features from Weeks 1-6
"""

import streamlit as st
import requests
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "dev-token-change-in-production"

# Page configuration
st.set_page_config(
    page_title="PythonMentor AI",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .code-output {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().timestamp()}"
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "beginner"

# Sidebar
with st.sidebar:
    st.image("https://www.python.org/static/community_logos/python-logo-generic.svg", width=200)
    st.title("🐍 PythonMentor AI")
    st.markdown("### Your AI Programming Tutor")
    
    st.markdown("---")
    
    # Difficulty selector
    difficulty = st.selectbox(
        "Learning Level",
        ["beginner", "intermediate", "advanced"],
        index=0,
        help="Select your current Python skill level"
    )
    st.session_state.difficulty = difficulty
    
    st.markdown("---")
    
    # Session info
    st.markdown("### 📊 Session Info")
    st.info(f"Session ID: {st.session_state.session_id[:8]}...")
    st.metric("Messages", len(st.session_state.messages))
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Features
    st.markdown("### ✨ Features")
    st.markdown("""
    - 💬 Interactive AI Tutoring
    - 🔧 Code Execution
    - 📝 Code Review
    - 🎯 Practice Quizzes
    - 📊 Progress Tracking
    - 🎤 Voice Input (Coming Soon)
    """)
    
    st.markdown("---")
    st.markdown("*Capstone Project: AI Coding Essentials*")

# Main content
st.markdown('<h1 class="main-header">🐍 PythonMentor AI</h1>', unsafe_allow_html=True)

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["💬 Tutor Chat", "🔧 Code Lab", "🎯 Quizzes", "📊 Progress"])

# TAB 1: TUTOR CHAT
with tab1:
    st.markdown("### Ask me anything about Python!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show code examples if available
            if "code_examples" in message and message["code_examples"]:
                st.markdown("**Code Examples:**")
                for code in message["code_examples"]:
                    st.code(code, language="python")
    
    # Input area
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Your question:", key="tutor_input", label_visibility="collapsed", 
                                   placeholder="Type your Python question here...")
    with col2:
        send_button = st.button("Send", key="send_btn", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get AI response
        try:
            response = requests.post(
                f"{API_BASE_URL}/tutor/chat",
                json={
                    "message": user_input,
                    "session_id": st.session_state.session_id,
                    "difficulty": st.session_state.difficulty,
                    "use_voice": False,
                    "context": []
                },
                headers={"Authorization": f"Bearer {API_TOKEN}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Add to session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["message"],
                    "code_examples": data.get("code_examples", [])
                })
                st.rerun()
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Note: Make sure the backend API is running on http://localhost:8000")

# TAB 2: CODE LAB
with tab2:
    st.markdown("### 🔧 Python Code Lab")
    st.markdown("Write and run Python code with instant feedback!")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### Your Code")
        code_input = st.text_area(
            "Write Python code here:",
            height=300,
            placeholder="# Write your Python code here\nprint('Hello, World!')",
            key="code_editor"
        )
        
        col_run, col_review = st.columns(2)
        
        with col_run:
            if st.button("▶️ Run Code", type="primary"):
                if code_input:
                    with st.spinner("Executing..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/code/execute",
                                json={
                                    "code": code_input,
                                    "session_id": st.session_state.session_id,
                                    "timeout": 5
                                },
                                headers={"Authorization": f"Bearer {API_TOKEN}"}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                if result.get("error"):
                                    st.error("❌ Execution failed")
                                    st.code(result["error"], language="text")
                                else:
                                    st.success("✅ Execution successful!")
                                    st.code(result["output"], language="text")
                                
                                st.info(f"⏱️ Execution time: {result['execution_time']:.3f}s")
                            else:
                                st.error(f"API Error: {response.status_code}")
                        
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please write some code first!")
        
        with col_review:
            if st.button("🔍 Review Code"):
                if code_input:
                    with st.spinner("Analyzing..."):
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/code/review",
                                json={
                                    "code": code_input,
                                    "focus_areas": ["style", "bugs", "performance"]
                                },
                                headers={"Authorization": f"Bearer {API_TOKEN}"}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                st.markdown("### 📊 Code Review")
                                st.metric("Overall Score", f"{result['overall_score']}/100")
                                
                                with st.expander("📝 Detailed Feedback"):
                                    st.markdown(result["summary"])
                        
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please write some code first!")
    
    with col2:
        st.markdown("#### Quick Examples")
        
        example = st.selectbox(
            "Load an example:",
            [
                "Hello World",
                "Variables",
                "Functions",
                "Lists",
                "Loops"
            ]
        )
        
        examples = {
            "Hello World": "# Hello World example\nprint('Hello, World!')",
            "Variables": "# Variables example\nname = 'Alice'\nage = 25\nprint(f'{name} is {age} years old')",
            "Functions": "# Function example\ndef greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Bob'))",
            "Lists": "# List example\nnumbers = [1, 2, 3, 4, 5]\nsquares = [x**2 for x in numbers]\nprint(squares)",
            "Loops": "# Loop example\nfor i in range(5):\n    print(f'Count: {i}')"
        }
        
        if st.button("Load Example"):
            st.session_state.code_editor = examples[example]
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("#### 💡 Tips")
        st.info("""
        - Write clean, readable code
        - Use descriptive variable names
        - Add comments to explain logic
        - Test your code with different inputs
        - Learn from the feedback!
        """)

# TAB 3: QUIZZES
with tab3:
    st.markdown("### 🎯 Practice Quizzes")
    st.markdown("Test your Python knowledge!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input("Quiz Topic", "Python Basics")
        quiz_difficulty = st.select_slider(
            "Difficulty",
            options=["easy", "medium", "hard"],
            value="medium"
        )
        num_questions = st.slider("Number of Questions", 3, 10, 5)
    
    if st.button("📝 Generate Quiz", type="primary"):
        with st.spinner("Generating quiz..."):
            st.info("Quiz generation feature - connect to backend API")
            st.markdown("*Sample quiz questions would appear here*")

# TAB 4: PROGRESS
with tab4:
    st.markdown("### 📊 Your Learning Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Topics Covered", "8")
        st.metric("Quizzes Completed", "3")
    
    with col2:
        st.metric("Average Score", "78%")
        st.metric("Code Submissions", "15")
    
    with col3:
        st.metric("Learning Time", "2.5 hrs")
        st.metric("Current Level", difficulty.capitalize())
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Recommended Next Steps")
    st.info("""
    1. Practice list comprehensions
    2. Learn about error handling
    3. Explore dictionaries and sets
    """)
    
    st.markdown("#### 💪 Your Strengths")
    st.success("""
    - Clear code structure
    - Good variable naming
    - Understanding of basic concepts
    """)
    
    st.markdown("#### 📚 Areas to Improve")
    st.warning("""
    - Error handling with try/except
    - Advanced list operations
    - Dictionary comprehensions
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ using Streamlit, FastAPI, LangGraph, and OpenAI</p>
    <p>Capstone Project - AI Coding Essentials Course</p>
</div>
""", unsafe_allow_html=True)
