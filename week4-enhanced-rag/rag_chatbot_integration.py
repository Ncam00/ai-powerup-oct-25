"""
Week 4 RAG-Enhanced Chatbot Integration
Connecting the enhanced RAG system with existing chatbot applications for knowledge-powered conversations
"""

import streamlit as st
import asyncio
import os
from typing import Dict, Any, List
from datetime import datetime

# Import the enhanced RAG system
from enhanced_rag_system import EnhancedRAGSystem

# LangChain imports for conversation memory
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.memory import ConversationBufferWindowMemory
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema.runnable import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain.callbacks import StreamlitCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    st.error("LangChain dependencies not available")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class RAGChatbot:
    """Enhanced chatbot with RAG capabilities and conversation memory"""
    
    def __init__(self):
        self.rag_system = None
        self.memory = None
        self.llm = None
        self.conversation_chain = None
        self.setup_complete = False
        
        # Initialize components
        self._initialize_rag()
        self._initialize_conversation_memory()
        self._initialize_llm()
        self._create_conversation_chain()
    
    def _initialize_rag(self):
        """Initialize the RAG system"""
        try:
            self.rag_system = EnhancedRAGSystem("chatbot_knowledge_base")
            st.success("✅ RAG system initialized")
        except Exception as e:
            st.error(f"❌ RAG system initialization failed: {e}")
            self.rag_system = None
    
    def _initialize_conversation_memory(self):
        """Initialize conversation memory for context"""
        try:
            self.memory = ConversationBufferWindowMemory(
                k=6,  # Remember last 6 exchanges
                memory_key="chat_history",
                return_messages=True
            )
            st.success("✅ Conversation memory initialized")
        except Exception as e:
            st.error(f"❌ Memory initialization failed: {e}")
            self.memory = None
    
    def _initialize_llm(self):
        """Initialize the language model"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.7,  # Balanced creativity for conversation
                streaming=True
            )
            st.success("✅ Language model initialized")
        except Exception as e:
            st.error(f"❌ LLM initialization failed: {e}")
            self.llm = None
    
    def _create_conversation_chain(self):
        """Create the conversation chain with RAG and memory"""
        if not all([self.rag_system, self.memory, self.llm]):
            st.warning("⚠️ Some components not available, limited functionality")
            return
        
        # Enhanced prompt that uses both RAG context and conversation history
        template = """You are a knowledgeable AI assistant with access to a comprehensive knowledge base and conversation memory.

        When answering questions:
        1. First check if relevant information is available in the knowledge base context
        2. Consider the conversation history for continuity and context
        3. Provide accurate, helpful responses based on available information
        4. If information is not available in your knowledge base, clearly state this and offer general guidance
        5. Maintain a conversational, friendly tone
        
        Knowledge Base Context (if relevant):
        {context}
        
        Conversation History:
        {chat_history}
        
        Current Question: {question}
        
        Response:"""
        
        self.conversation_prompt = ChatPromptTemplate.from_template(template)
        
        try:
            # Create the enhanced conversation chain
            self.conversation_chain = (
                {
                    "context": RunnablePassthrough(),
                    "chat_history": lambda x: self.memory.chat_memory.messages,
                    "question": RunnablePassthrough()
                }
                | self.conversation_prompt
                | self.llm
                | StrOutputParser()
            )
            
            self.setup_complete = True
            st.success("✅ RAG-enhanced conversation chain created")
            
        except Exception as e:
            st.error(f"❌ Conversation chain creation failed: {e}")
    
    def get_rag_context(self, question: str) -> str:
        """Retrieve relevant context from RAG system"""
        if not self.rag_system:
            return "Knowledge base not available."
        
        try:
            # Query the RAG system for relevant context
            result = self.rag_system.query_with_analysis(question, retriever_type="mmr")
            
            if "error" in result:
                return "Could not retrieve relevant context from knowledge base."
            
            # Extract and format the context
            context_info = result.get("context_analysis", {})
            answer = result.get("answer", "")
            
            # Create a summary of the context
            context_summary = f"Based on {context_info.get('num_chunks', 0)} relevant documents"
            if context_info.get("sources"):
                unique_sources = len(set(context_info["sources"]))
                context_summary += f" from {unique_sources} sources"
            
            return f"{context_summary}: {answer}"
            
        except Exception as e:
            return f"Error retrieving context: {e}"
    
    def chat_with_rag(self, user_message: str) -> str:
        """Process a chat message with RAG enhancement"""
        
        if not self.setup_complete:
            return "❌ Chatbot not properly initialized. Please check the setup."
        
        try:
            # Get RAG context for the question
            rag_context = self.get_rag_context(user_message)
            
            # Prepare input for the conversation chain
            chain_input = {
                "context": rag_context,
                "question": user_message
            }
            
            # Generate response using the conversation chain
            response = self.conversation_chain.invoke(chain_input)
            
            # Store the conversation in memory
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(response)
            
            return response
            
        except Exception as e:
            return f"❌ Error processing message: {e}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get formatted conversation history"""
        if not self.memory:
            return []
        
        history = []
        messages = self.memory.chat_memory.messages
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                human_msg = messages[i]
                ai_msg = messages[i + 1]
                
                history.append({
                    "human": human_msg.content,
                    "ai": ai_msg.content,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
        
        return history
    
    def clear_conversation(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
    
    def get_system_status(self) -> Dict[str, str]:
        """Get status of all system components"""
        status = {
            "RAG System": "✅ Connected" if self.rag_system else "❌ Not available",
            "Conversation Memory": "✅ Active" if self.memory else "❌ Not available",
            "Language Model": "✅ Ready" if self.llm else "❌ Not available",
            "Conversation Chain": "✅ Ready" if self.conversation_chain else "❌ Not available",
            "Overall Status": "✅ Ready" if self.setup_complete else "⚠️ Limited functionality"
        }
        
        return status


def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="RAG-Enhanced Knowledge Chatbot",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 RAG-Enhanced Knowledge Chatbot")
    st.markdown("*Powered by Enhanced RAG System + Conversation Memory*")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing RAG-enhanced chatbot..."):
            st.session_state.chatbot = RAGChatbot()
    
    chatbot = st.session_state.chatbot
    
    # Sidebar with system information
    with st.sidebar:
        st.header("🔧 System Status")
        
        status = chatbot.get_system_status()
        for component, state in status.items():
            st.write(f"**{component}:** {state}")
        
        st.divider()
        
        # RAG system information
        if chatbot.rag_system:
            st.header("📚 Knowledge Base Info")
            rag_status = chatbot.rag_system.get_system_status()
            
            st.write(f"**Documents:** {rag_status['document_stats']['total_chunks']} chunks")
            st.write(f"**File Types:** {', '.join(rag_status['document_stats']['file_types'].keys())}")
            st.write(f"**Retrievers:** {len(rag_status['retrievers_available'])} strategies")
        
        st.divider()
        
        # Conversation controls
        st.header("💬 Conversation")
        
        if st.button("🗑️ Clear History", help="Clear conversation memory"):
            chatbot.clear_conversation()
            st.rerun()
        
        # Display conversation statistics
        history = chatbot.get_conversation_history()
        st.write(f"**Messages:** {len(history) * 2}")
        st.write(f"**Memory:** {len(history)}/6 exchanges")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Chat input
        user_input = st.chat_input("Ask me anything about the knowledge base...")
        
        if user_input:
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Generate and display AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chatbot.chat_with_rag(user_input)
                st.write(response)
        
        # Display conversation history
        st.subheader("📜 Conversation History")
        
        history = chatbot.get_conversation_history()
        
        if history:
            for exchange in reversed(history[-5:]):  # Show last 5 exchanges
                with st.expander(f"🕐 {exchange['timestamp']} - {exchange['human'][:50]}..."):
                    st.write(f"**You:** {exchange['human']}")
                    st.write(f"**Assistant:** {exchange['ai']}")
        else:
            st.info("No conversation history yet. Start chatting!")
    
    with col2:
        st.header("🎯 Quick Examples")
        
        example_questions = [
            "What are the penalties for breaching the EU AI Act?",
            "How are AI systems classified by risk level?",
            "What AI practices are prohibited in the EU?",
            "How do recruitment laws apply to AI?",
            "What are the key compliance requirements?"
        ]
        
        st.write("Try these example questions:")
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.example_question = question
                st.rerun()
        
        # Handle example question selection
        if hasattr(st.session_state, 'example_question'):
            user_input = st.session_state.example_question
            delattr(st.session_state, 'example_question')
            
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.chat_message("assistant"):
                with st.spinner("Processing example question..."):
                    response = chatbot.chat_with_rag(user_input)
                st.write(response)
        
        st.divider()
        
        st.header("📊 Features")
        st.write("""
        **🧠 RAG-Enhanced Knowledge:**
        - Multi-format document processing
        - Advanced retrieval strategies
        - Context quality analysis
        
        **💭 Conversation Memory:**
        - Maintains context across messages
        - Remembers last 6 exchanges
        - Smooth conversation flow
        
        **🔍 Advanced Retrieval:**
        - MMR (Maximal Marginal Relevance)
        - Multiple similarity strategies
        - Source attribution and confidence
        
        **📈 Observability:**
        - Langfuse tracing integration
        - Performance monitoring
        - Quality assessment
        """)


def demo_rag_chatbot_integration():
    """Standalone demo function"""
    
    print("Week 4 RAG-Enhanced Chatbot Integration Demo")
    print("=" * 60)
    
    print("🧠 RAG Chatbot Features:")
    print("✅ Enhanced RAG system with multi-format document support")
    print("✅ Conversation memory for contextual responses")
    print("✅ Advanced retrieval with MMR and similarity strategies")
    print("✅ Real-time system status monitoring")
    print("✅ Example questions and user-friendly interface")
    print("✅ Comprehensive observability and tracing")
    
    print("\n🎯 Integration Benefits:")
    print("- Combines knowledge base power with conversational AI")
    print("- Maintains conversation context across multiple exchanges")
    print("- Provides source attribution and confidence levels")
    print("- Enables complex multi-turn knowledge exploration")
    
    print("\n🚀 To run the chatbot interface:")
    print("streamlit run rag_chatbot_integration.py")


if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "demo":
        demo_rag_chatbot_integration()
    else:
        main()