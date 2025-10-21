"""
LangChain Chatbot with Streamlit Interface
A simple AI chatbot using LangChain and Streamlit with streaming responses.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks.base import BaseCallbackHandler
import time

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
        self.container.markdown(self.text + "▌")  # Show cursor while typing

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")

def setup_llm(api_key: str, streaming: bool = True):
    """Set up the LangChain LLM with streaming capability"""
    if not api_key:
        st.error("Please provide an OpenAI API key!")
        st.stop()
    
    return ChatOpenAI(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=0.7,
        streaming=streaming
    )

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="LangChain Chatbot",
        page_icon="🤖",
        layout="centered"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 LangChain Chatbot")
    st.markdown("*Powered by LangChain and Streamlit*")
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_api_key,
            help="Enter your OpenAI API key"
        )
        
        if api_key:
            st.session_state.openai_api_key = api_key
        
        st.markdown("---")
        st.markdown("### How to use:")
        st.markdown("""
        1. Enter your OpenAI API key above
        2. Type your message in the chat box
        3. Watch the AI respond in real-time!
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    if not st.session_state.openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to start chatting!")
        st.info("You can get an API key from [OpenAI's website](https://platform.openai.com/api-keys)")
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
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response with streaming
        with st.chat_message("assistant"):
            # Create placeholder for streaming response
            message_placeholder = st.empty()
            
            try:
                # Set up LLM
                llm = setup_llm(st.session_state.openai_api_key)
                
                # Create streaming callback
                callback_handler = StreamlitCallbackHandler(message_placeholder)
                
                # Prepare conversation history for context
                conversation_messages = []
                for msg in st.session_state.messages[-10:]:  # Keep last 10 messages for context
                    conversation_messages.append(msg)
                
                # Get response with streaming
                response = ""
                for chunk in llm.stream([user_message]):
                    if hasattr(chunk, 'content'):
                        response += chunk.content
                        message_placeholder.markdown(response + "▌")
                
                # Final response without cursor
                message_placeholder.markdown(response)
                
                # Add AI response to chat history
                ai_message = AIMessage(content=response)
                st.session_state.messages.append(ai_message)
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Make sure your API key is valid and you have sufficient credits.")

if __name__ == "__main__":
    main()