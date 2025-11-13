"""
RAG-Enhanced Chatbot - Week 4 Integration
Combines the Enhanced Chatbot with RAG capabilities for knowledge-enhanced conversations
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

# Add the RAG system to path
sys.path.append(str(Path(__file__).parent.parent / "week4-enhanced-rag"))

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Import our enhanced RAG system
try:
    from enhanced_rag_system import EnhancedRAGSystem
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    st.error("RAG system not available. Please check the enhanced_rag_system.py file.")

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
        current_time = time.time()
        if current_time - self.last_update > 0.05:
            self.container.markdown(self.text + "▌")
            self.last_update = current_time

class RAGEnhancedChatbot:
    """Chatbot enhanced with RAG capabilities for knowledge-based conversations"""
    
    def __init__(self):
        self.rag_system = None
        self.conversation_memory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
            memory_key="chat_history"
        )
        self.initialize_rag()
    
    def initialize_rag(self):
        """Initialize the RAG system if available"""
        if RAG_AVAILABLE:
            try:
                self.rag_system = EnhancedRAGSystem()
                # Try to initialize with existing knowledge base
                if hasattr(self.rag_system, 'initialize_system'):
                    self.rag_system.initialize_system()
                return True
            except Exception as e:
                st.warning(f"RAG system initialization failed: {str(e)}")
                return False
        return False
    
    def get_relevant_context(self, query: str, num_docs: int = 3) -> str:
        """Retrieve relevant context from the knowledge base"""
        if not self.rag_system:
            return ""
        
        try:
            # Use the RAG system to get relevant documents
            if hasattr(self.rag_system, 'enhanced_retrieve'):
                docs = self.rag_system.enhanced_retrieve(query, k=num_docs)
            elif hasattr(self.rag_system, 'vectorstore') and self.rag_system.vectorstore:
                docs = self.rag_system.vectorstore.similarity_search(query, k=num_docs)
            else:
                return ""
            
            if docs:
                context_pieces = []
                for i, doc in enumerate(docs, 1):
                    content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                    source = doc.metadata.get('source', 'Unknown') if hasattr(doc, 'metadata') else 'Unknown'
                    context_pieces.append(f"[Source {i}: {source}]\n{content}")
                
                return "\n\n".join(context_pieces)
            
        except Exception as e:
            st.warning(f"Error retrieving context: {str(e)}")
            return ""
        
        return ""
    
    def create_enhanced_prompt(self, conversation_style: str, use_rag: bool = True):
        """Create prompt template with optional RAG context"""
        
        style_prompts = {
            "helpful": "You are a helpful and knowledgeable AI assistant.",
            "creative": "You are a creative and imaginative AI assistant.",
            "technical": "You are a technical expert AI assistant.",
            "casual": "You are a casual and friendly AI assistant.",
            "educational": "You are an educational AI tutor."
        }
        
        base_system = style_prompts.get(conversation_style, style_prompts["helpful"])
        
        if use_rag and self.rag_system:
            system_message = f"""{base_system}

You have access to a personal knowledge base that contains relevant information. When answering questions:

1. First check if the provided context is relevant to the user's question
2. If relevant context is provided, use it to enhance your answer
3. Always cite sources when using information from the knowledge base
4. If the context isn't relevant or sufficient, rely on your general knowledge
5. Be clear about when you're using information from the knowledge base vs general knowledge

Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONTEXT FROM KNOWLEDGE BASE:
{"{context}"}

Guidelines:
- Be engaging and conversational
- Ask follow-up questions when appropriate  
- Provide examples to illustrate points
- If unsure, say so and suggest how to find more information
- Keep responses focused but comprehensive"""
        else:
            system_message = f"""{base_system}
            
Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Guidelines:
- Be engaging and conversational
- Ask follow-up questions when appropriate
- Provide examples to illustrate points
- If you're unsure about something, say so
- Keep responses focused but comprehensive"""
        
        if use_rag and self.rag_system:
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
        
        return prompt
    
    def create_conversation_chain(self, api_key: str, model_provider: str, 
                                conversation_style: str, temperature: float, use_rag: bool):
        """Create the enhanced conversation chain with optional RAG"""
        
        # Initialize LLM based on provider
        if model_provider == "OpenAI" and api_key:
            llm = ChatOpenAI(
                api_key=api_key,
                model="gpt-3.5-turbo",
                temperature=temperature,
                streaming=True
            )
        elif model_provider == "Google Gemini":
            google_api_key = os.getenv("GOOGLE_API_KEY") or api_key
            if google_api_key:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=google_api_key,
                    temperature=temperature
                )
            else:
                st.error("Google API key required for Gemini")
                return None
        else:
            st.error("Please provide a valid API key and select a model provider")
            return None
        
        prompt = self.create_enhanced_prompt(conversation_style, use_rag)
        
        if use_rag and self.rag_system:
            # Create chain with RAG context retrieval
            def get_context_and_history(inputs):
                context = self.get_relevant_context(inputs["input"])
                chat_history = self.conversation_memory.load_memory_variables({})["chat_history"]
                return {
                    "context": context,
                    "chat_history": chat_history,
                    "input": inputs["input"]
                }
            
            chain = (
                RunnablePassthrough.assign(context=lambda x: self.get_relevant_context(x["input"])) |
                RunnablePassthrough.assign(chat_history=lambda x: self.conversation_memory.load_memory_variables({})["chat_history"]) |
                prompt |
                llm |
                StrOutputParser()
            )
        else:
            # Standard chain without RAG
            chain = (
                RunnablePassthrough.assign(
                    chat_history=lambda x: self.conversation_memory.load_memory_variables({})["chat_history"]
                ) |
                prompt |
                llm |
                StrOutputParser()
            )
        
        return chain

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if "conversation_style" not in st.session_state:
        st.session_state.conversation_style = "helpful"
    if "model_temperature" not in st.session_state:
        st.session_state.model_temperature = 0.7
    if "model_provider" not in st.session_state:
        st.session_state.model_provider = "OpenAI"
    if "use_rag" not in st.session_state:
        st.session_state.use_rag = True
    if "rag_chatbot" not in st.session_state:
        st.session_state.rag_chatbot = RAGEnhancedChatbot()

def render_sidebar():
    """Render enhanced sidebar with RAG controls"""
    with st.sidebar:
        st.title("Enhanced RAG Chatbot")
        
        # API Configuration
        st.subheader("API Configuration")
        
        model_provider = st.selectbox(
            "Model Provider:",
            ["OpenAI", "Google Gemini"],
            index=0 if st.session_state.model_provider == "OpenAI" else 1
        )
        st.session_state.model_provider = model_provider
        
        if model_provider == "OpenAI":
            api_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.openai_api_key,
                type="password",
                help="Enter your OpenAI API key"
            )
            st.session_state.openai_api_key = api_key
        else:
            google_key = st.text_input(
                "Google API Key",
                value=os.getenv("GOOGLE_API_KEY", ""),
                type="password",
                help="Enter your Google API key for Gemini"
            )
        
        st.divider()
        
        # RAG Configuration
        st.subheader("Knowledge Enhancement")
        use_rag = st.checkbox(
            "Enable Knowledge Base",
            value=st.session_state.use_rag,
            help="Use your personal knowledge base to enhance responses"
        )
        st.session_state.use_rag = use_rag
        
        if use_rag and RAG_AVAILABLE:
            if st.session_state.rag_chatbot.rag_system:
                st.success("Knowledge base connected")
                
                # RAG Settings
                with st.expander("RAG Settings"):
                    st.info("Knowledge base is active and will be used to enhance responses with relevant context from your documents.")
            else:
                st.warning("Knowledge base not available")
        elif use_rag and not RAG_AVAILABLE:
            st.error("RAG system not available")
        
        st.divider()
        
        # Conversation Settings
        st.subheader("Conversation Style")
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
        temperature = st.slider(
            "Response creativity:",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.model_temperature,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        st.session_state.model_temperature = temperature
        
        st.divider()
        
        # Conversation Stats
        st.subheader("Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        if st.session_state.rag_chatbot.conversation_memory:
            memory_vars = st.session_state.rag_chatbot.conversation_memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            st.metric("Memory Buffer", len(chat_history))
        
        # Clear conversation
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.rag_chatbot.conversation_memory.clear()
            st.rerun()

def render_chat_interface():
    """Render the enhanced chat interface"""
    # Title with RAG indicator
    rag_indicator = "🧠" if st.session_state.use_rag and RAG_AVAILABLE else "💬"
    st.title(f"RAG-Enhanced Chatbot {rag_indicator}")
    
    if not st.session_state.openai_api_key and st.session_state.model_provider == "OpenAI":
        st.warning("Please enter your OpenAI API key in the sidebar to start chatting!")
        return
    
    if st.session_state.use_rag and RAG_AVAILABLE:
        if st.session_state.rag_chatbot.rag_system:
            st.info("💡 Knowledge base is active - I can use your personal documents to enhance my responses!")
        else:
            st.warning("⚠️ Knowledge base connection failed - falling back to standard chat mode")
    
    # Display chat messages
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(message.content)
    
    # Chat input
    if not st.session_state.messages:
        if st.session_state.use_rag and RAG_AVAILABLE:
            st.info("💡 Try asking: 'What do you know about [topic from my documents]?' or 'Search my notes for information about...'")
        else:
            st.info("💡 Try asking: 'Explain Python decorators' or 'Help me plan a project'")
    
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Create conversation chain
                chain = st.session_state.rag_chatbot.create_conversation_chain(
                    api_key=st.session_state.openai_api_key,
                    model_provider=st.session_state.model_provider,
                    conversation_style=st.session_state.conversation_style,
                    temperature=st.session_state.model_temperature,
                    use_rag=st.session_state.use_rag
                )
                
                if chain:
                    # Generate response
                    response = ""
                    for chunk in chain.stream({"input": prompt}):
                        response += chunk
                        message_placeholder.markdown(response + "▌")
                    
                    # Final response
                    message_placeholder.markdown(response)
                    
                    # Add to conversation memory and messages
                    ai_message = AIMessage(content=response)
                    st.session_state.messages.append(ai_message)
                    
                    # Update memory
                    st.session_state.rag_chatbot.conversation_memory.save_context(
                        {"input": prompt},
                        {"output": response}
                    )
                else:
                    st.error("Failed to create conversation chain. Please check your API key.")
                    
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.info("Please check your API key and try again.")

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="RAG-Enhanced Chatbot",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    # Create layout
    col1, col2 = st.columns([3, 1])
    
    with col2:
        render_sidebar()
    
    with col1:
        render_chat_interface()

if __name__ == "__main__":
    main()