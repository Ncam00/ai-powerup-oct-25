"""
PythonMentor AI - Intelligent Python Programming Tutor
A specialized AI tutor for learning Python programming through conversation and practice.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.callbacks.base import BaseCallbackHandler
import re

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
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None

def get_tutor_system_prompt(level: str) -> str:
    """Create system prompt for Python tutor based on student level"""
    base_prompt = """You are PythonMentor AI, an expert Python programming tutor. Your teaching philosophy:

1. **Socratic Method**: Ask guiding questions to help students discover answers
2. **Learn by Doing**: Provide hands-on examples and coding exercises  
3. **Mistake-Friendly**: Encourage experimentation and learning from errors
4. **Clear Explanations**: Break down complex concepts into simple steps
5. **Practical Focus**: Use real-world examples and applicable code

"""
    
    level_prompts = {
        "beginner": """
**Student Level: Complete Beginner**
- Assume no prior programming experience
- Explain basic concepts like variables, data types, and syntax
- Use simple analogies and everyday examples
- Encourage and be very patient with basic questions
- Start with fundamental concepts before moving to advanced topics
""",
        "intermediate": """
**Student Level: Some Programming Experience**
- Student knows basic syntax and concepts
- Focus on functions, data structures, and object-oriented programming
- Provide more complex examples and debugging challenges
- Encourage best practices and code efficiency
- Bridge gaps between basic and advanced concepts
""",
        "advanced": """
**Student Level: Experienced Programmer**  
- Student has solid Python fundamentals
- Focus on advanced topics, optimization, and best practices
- Discuss design patterns, libraries, and professional development
- Provide challenging problems and code review
- Explore Python's advanced features and ecosystem
"""
    }
    
    teaching_guidelines = """
**Teaching Guidelines:**
- Always explain your reasoning when solving problems
- If student shows code with errors, guide them to find the solution rather than just giving the answer
- Use code examples frequently to illustrate concepts
- Ask "Does this make sense?" or "Do you want to try this?" regularly
- When appropriate, suggest small coding exercises to practice concepts
- Celebrate student progress and breakthroughs
- If a concept seems unclear, try explaining it a different way

**Code Formatting:**
- Use proper Python code blocks with syntax highlighting
- Include comments in code examples to explain what's happening
- Show both the code and expected output when helpful

Remember: Your goal is to help the student become a confident, independent Python programmer!
"""
    
    return base_prompt + level_prompts.get(level, level_prompts["beginner"]) + teaching_guidelines

def setup_llm(api_key: str, student_level: str, streaming: bool = True):
    """Set up the LangChain LLM for Python tutoring"""
    if not api_key:
        st.error("Please provide an OpenAI API key!")
        st.stop()
    
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-4",
        temperature=0.7,
        streaming=streaming
    )

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="PythonMentor AI",
        page_icon="🐍",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🐍 PythonMentor AI")
    st.markdown("*Your Personal Python Programming Tutor*")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🎓 Learning Configuration")
        
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
        
        # Student level selection
        st.session_state.student_level = st.selectbox(
            "Your Programming Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.student_level),
            help="This helps the tutor adjust explanations to your level"
        )
        
        st.markdown("---")
        
        # Learning progress
        st.subheader("📚 Learning Progress")
        if st.session_state.topics_covered:
            st.write("**Topics Covered:**")
            for topic in sorted(st.session_state.topics_covered):
                st.write(f"✅ {topic}")
        else:
            st.write("*No topics covered yet - start chatting to begin learning!*")
        
        if st.button("Reset Learning Progress"):
            st.session_state.topics_covered = set()
            st.session_state.current_topic = None
            st.rerun()
        
        st.markdown("---")
        
        # Quick start suggestions
        st.subheader("💡 Learning Suggestions")
        suggestions = {
            "beginner": [
                "What is a variable in Python?",
                "How do I create a list?", 
                "What's the difference between print() and return?",
                "Can you show me how to write a simple function?"
            ],
            "intermediate": [
                "How do I handle exceptions properly?",
                "What's the difference between a list and a tuple?",
                "Can you explain how classes work?",
                "How do I read data from a CSV file?"
            ],
            "advanced": [
                "What are Python decorators and how do I use them?",
                "How do I optimize slow Python code?",
                "Can you explain list comprehensions vs generator expressions?",
                "What are the best practices for organizing larger projects?"
            ]
        }
        
        level_suggestions = suggestions.get(st.session_state.student_level, suggestions["beginner"])
        for suggestion in level_suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion[:20]}"):
                # Add suggestion as user message
                user_message = HumanMessage(content=suggestion)
                st.session_state.messages.append(user_message)
                st.rerun()
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    if not st.session_state.openai_api_key:
        st.warning("🔑 Please enter your OpenAI API key in the sidebar to start learning Python!")
        st.info("You can get an API key from [OpenAI's website](https://platform.openai.com/api-keys)")
        
        # Show some example content
        st.markdown("### 🐍 What You'll Learn")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔤 Python Fundamentals**
            - Variables and data types
            - Control structures (if, for, while)
            - Functions and scope
            - Input/output operations
            """)
        
        with col2:
            st.markdown("""
            **📊 Data Structures** 
            - Lists, tuples, dictionaries
            - String manipulation
            - File handling
            - Error handling
            """)
        
        with col3:
            st.markdown("""
            **🏗️ Advanced Concepts**
            - Object-oriented programming
            - Libraries and modules
            - Best practices
            - Debugging techniques
            """)
        
        return
    
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
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Set up LLM with tutoring system prompt
                llm = setup_llm(st.session_state.openai_api_key, st.session_state.student_level)
                
                # Create system message with tutor instructions
                system_message = SystemMessage(content=get_tutor_system_prompt(st.session_state.student_level))
                
                # Prepare conversation history (include system message)
                conversation_messages = [system_message]
                
                # Add recent conversation history for context (last 10 messages)
                recent_messages = st.session_state.messages[-10:]
                conversation_messages.extend(recent_messages)
                
                # Get streaming response
                response = ""
                for chunk in llm.stream(conversation_messages):
                    if hasattr(chunk, 'content'):
                        response += chunk.content
                        message_placeholder.markdown(response + "▌")
                
                # Final response without cursor
                message_placeholder.markdown(response)
                
                # Add AI response to chat history
                ai_message = AIMessage(content=response)
                st.session_state.messages.append(ai_message)
                
                # Simple topic tracking (extract potential Python topics from the conversation)
                python_topics = [
                    "variables", "functions", "lists", "dictionaries", "loops", "conditionals",
                    "classes", "objects", "exceptions", "files", "strings", "tuples", "sets"
                ]
                
                prompt_lower = prompt.lower()
                for topic in python_topics:
                    if topic in prompt_lower or topic in response.lower():
                        st.session_state.topics_covered.add(topic.title())
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Make sure your API key is valid and you have sufficient credits.")

if __name__ == "__main__":
    main()