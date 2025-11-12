"""
Enhanced LangChain Chatbot with Advanced Features
Demonstrates advanced LangChain concepts: memory, prompt templates, and conversation chains
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Enhanced callback handler for streaming responses to Streamlit"""
    
    def __init__(self, container):
        self.container = container
        self.text = ""
        self.last_update = time.time()
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.text += token
        # Update UI more efficiently - only every 50ms
        current_time = time.time()
        if current_time - self.last_update > 0.05:
            self.container.markdown(self.text + "▌")
            self.last_update = current_time

def initialize_session_state():
    """Initialize Streamlit session state variables with enhanced features"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
    if "conversation_style" not in st.session_state:
        st.session_state.conversation_style = "helpful"
    if "model_temperature" not in st.session_state:
        st.session_state.model_temperature = 0.7

def create_enhanced_prompt():
    """Create an enhanced prompt template with personality and context"""
    system_prompts = {
        "helpful": "You are a helpful and friendly AI assistant. Provide clear, accurate, and detailed responses. Be encouraging and supportive.",
        "creative": "You are a creative and imaginative AI assistant. Think outside the box, provide unique perspectives, and use creative analogies and examples.",
        "technical": "You are a technical expert AI assistant. Provide precise, detailed technical information with examples, code snippets when relevant, and step-by-step explanations.",
        "casual": "You are a casual and fun AI assistant. Use a relaxed conversational tone, include humor when appropriate, and make the conversation enjoyable.",
        "educational": "You are an educational AI tutor. Break down complex topics into understandable parts, ask follow-up questions to ensure comprehension, and provide learning resources."
    }
    
    system_message = system_prompts.get(st.session_state.conversation_style, system_prompts["helpful"])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""{system_message}
        
Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Guidelines:
- Be engaging and conversational
- Ask follow-up questions when appropriate
- Provide examples to illustrate points
- If you're unsure about something, say so
- Format code snippets with proper markdown
- Keep responses focused but comprehensive"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    return prompt

def setup_enhanced_llm(api_key: str):
    """Set up the enhanced LangChain conversation chain"""
    if not api_key:
        st.error("Please provide an OpenAI API key!")
        st.stop()
    
    # Create the LLM
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-3.5-turbo",
        temperature=st.session_state.model_temperature,
        streaming=True
    )
    
    # Create the enhanced prompt
    prompt = create_enhanced_prompt()
    
    # Create the conversation chain with memory
    chain = (
        RunnablePassthrough.assign(
            chat_history=lambda x: st.session_state.conversation_memory.load_memory_variables({})["chat_history"]
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def render_sidebar():
    """Render enhanced sidebar with conversation controls"""
    with st.sidebar:
        st.title("🤖 Chat Settings")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Enter your OpenAI API key"
        )
        st.session_state.openai_api_key = api_key
        
        st.divider()
        
        # Conversation style selector
        st.subheader("🎭 Conversation Style")
        styles = {
            "helpful": "💡 Helpful & Supportive",
            "creative": "🎨 Creative & Imaginative", 
            "technical": "🔧 Technical Expert",
            "casual": "😊 Casual & Fun",
            "educational": "📚 Educational Tutor"
        }
        
        selected_style = st.selectbox(
            "Choose conversation style:",
            options=list(styles.keys()),
            format_func=lambda x: styles[x],
            index=list(styles.keys()).index(st.session_state.conversation_style)
        )
        st.session_state.conversation_style = selected_style
        
        # Temperature control
        st.subheader("🌡️ Creativity Level")
        temperature = st.slider(
            "Response creativity (temperature):",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.model_temperature,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        st.session_state.model_temperature = temperature
        
        st.divider()
        
        # Conversation stats
        st.subheader("📊 Conversation Stats")
        st.metric("Messages", len(st.session_state.messages))
        if st.session_state.conversation_memory:
            memory_vars = st.session_state.conversation_memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            st.metric("Memory Buffer", len(chat_history))
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.conversation_memory.clear()
            st.rerun()
        
        # Export conversation
        if st.session_state.messages and st.button("💾 Export Chat"):
            chat_export = ""
            for msg in st.session_state.messages:
                if isinstance(msg, HumanMessage):
                    chat_export += f"User: {msg.content}\n\n"
                elif isinstance(msg, AIMessage):
                    chat_export += f"Assistant: {msg.content}\n\n"
            
            st.download_button(
                label="📄 Download Chat History",
                data=chat_export,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def render_chat_interface():
    """Render the enhanced chat interface"""
    # Chat title with style indicator
    style_icons = {
        "helpful": "💡", "creative": "🎨", "technical": "🔧", 
        "casual": "😊", "educational": "📚"
    }
    current_icon = style_icons.get(st.session_state.conversation_style, "💡")
    st.title(f"LangChain Enhanced Chatbot {current_icon}")
    
    if not st.session_state.openai_api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start chatting!")
        return
    
    # Display chat messages with enhanced formatting
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
    
    # Chat input with example prompts
    if not st.session_state.messages:
        st.info("💡 Try asking: 'Explain Python decorators' or 'Help me plan a project' or 'Tell me a creative story'")
    
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Add to memory
        st.session_state.conversation_memory.save_context(
            {"input": prompt},
            {"output": ""}  # Will be filled when response is generated
        )
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response with enhanced streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Set up enhanced conversation chain
                chain = setup_enhanced_llm(st.session_state.openai_api_key)
                
                # Generate response
                response = ""
                for chunk in chain.stream({"input": prompt}):
                    response += chunk
                    message_placeholder.markdown(response + "▌")
                
                # Final response without cursor
                message_placeholder.markdown(response)
                
                # Add AI response to chat history and memory
                ai_message = AIMessage(content=response)
                st.session_state.messages.append(ai_message)
                
                # Update memory with complete response
                if st.session_state.conversation_memory.chat_memory.messages:
                    st.session_state.conversation_memory.chat_memory.messages[-1] = ai_message
                
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.info("💡 Make sure your API key is valid and you have sufficient credits.")

def main():
    """Enhanced main Streamlit application"""
    st.set_page_config(
        page_title="Enhanced LangChain Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Create layout
    col1, col2 = st.columns([3, 1])
    
    with col2:
        render_sidebar()
    
    with col1:
        render_chat_interface()

if __name__ == "__main__":
    main()