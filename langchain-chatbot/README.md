# 🤖 LangChain Chatbot

A modern AI chatbot built with **LangChain** and **Streamlit** featuring real-time streaming responses.

## ✨ Features

- **Real-time streaming responses** - See the AI type responses in real-time
- **Clean web interface** - Built with Streamlit for easy interaction
- **Conversation memory** - Maintains context across the conversation
- **Configurable** - Easy API key setup and model selection
- **Error handling** - Graceful error messages and recovery

## 🚀 Quick Start

### 1. Clone and Setup
```bash
cd /root/overview/langchain-chatbot
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Chatbot
```bash
streamlit run app.py
```

## 🛠️ How It Works

### LangChain Integration
- Uses `ChatOpenAI` for LLM interactions
- Implements streaming callbacks for real-time responses
- Manages conversation history with `HumanMessage` and `AIMessage`

### Streamlit Interface
- Clean chat interface with `st.chat_message()`
- Sidebar configuration for API keys
- Session state management for conversation persistence

### Key Components

**Main App (`app.py`):**
- `StreamlitCallbackHandler` - Custom streaming handler
- `setup_llm()` - LangChain model configuration
- `main()` - Streamlit app logic

## 📚 Learning Objectives Met

✅ **LangChain Integration** - Using ChatOpenAI and message types  
✅ **Streamlit Web Interface** - Interactive chat UI  
✅ **Streaming Responses** - Real-time message display  
✅ **Error Handling** - Graceful API key and connection errors  
✅ **Session Management** - Conversation history persistence  

## 🔧 Technical Details

- **Framework**: LangChain + Streamlit
- **LLM Provider**: OpenAI GPT-3.5-turbo
- **Streaming**: Custom Streamlit callback handler
- **State Management**: Streamlit session state
- **Memory**: Last 10 messages for context

## 🎯 Week 2 Exercise Completion

This project fulfills the "Build a LangChain Chatbot" exercise requirements:
- ✅ Functional AI chatbot
- ✅ LangChain integration  
- ✅ Streaming responses
- ✅ Web interface with Streamlit
- ✅ Proper error handling

## 🚀 Next Steps

- Add web browsing capabilities (optional enhancement)
- Implement different LLM providers (Anthropic, etc.)
- Add conversation export functionality
- Enhance UI with custom CSS
