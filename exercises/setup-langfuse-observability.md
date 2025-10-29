# Setup Langfuse Observability for LangChain Applications

In this exercise, you'll learn to implement comprehensive observability for LangChain applications using Langfuse. You'll explore both the callback handler approach and the recommended LangChain wrapper for easier integration.

## Learning Goals

By the end of this exercise, you will:
- Set up Langfuse cloud service and understand observability concepts
- Use the LangChain wrapper for seamless Langfuse integration (recommended approach)
- Implement tracing for LangChain chains, agents, and tools
- Monitor conversation flows, token usage, and performance metrics
- Analyze application behavior using Langfuse dashboard and analytics
- Debug AI application issues using trace exploration and timeline visualization
- Set up evaluation frameworks to assess AI component quality

## Prerequisites

- Python 3.11+ installed
- LangChain application or willingness to create a simple one
- Google API key or other LLM provider access
- Basic familiarity with LangChain concepts

## Part 1: Setup Langfuse Cloud Service

### Step 1: Create a Langfuse Account
1. Go to [cloud.langfuse.com](https://cloud.langfuse.com) and sign up for a free account
2. Create a new project called "AICE Observability Demo"
3. Navigate to project settings and generate API credentials
4. Copy your `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`

### Step 2: Install Dependencies
```bash
# Install Langfuse with LangChain integration
pip install langfuse[langchain] langchain-google-genai python-dotenv

# Or if using uv
uv add langfuse[langchain] langchain-google-genai python-dotenv
```

### Step 3: Configure Environment
Create a `.env` file with your credentials:
```
GOOGLE_API_KEY="your-google-api-key"
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
```

## Part 2: LangChain Wrapper Approach (Recommended)

The LangChain wrapper provides the easiest way to add Langfuse observability to your applications. It automatically handles tracing configuration and provides a clean interface.

### Step 4: Create a Simple LangChain Application
Create `langchain_demo.py` to demonstrate observability:

```python
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def create_simple_chain():
    """Create a simple LangChain chain"""
    
    # Create components
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Answer the following question: {question}"
    )
    
    output_parser = StrOutputParser()
    
    # Create chain
    chain = prompt | llm | output_parser
    
    return chain

def main():
    """Test the chain without observability first"""
    chain = create_simple_chain()
    
    response = chain.invoke({"question": "What is the capital of France?"})
    print(f"Response: {response}")

if __name__ == "__main__":
    main()
```

### Step 5: Add Langfuse Wrapper Integration
Now modify the application to use Langfuse wrapper:

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import Langfuse LangChain wrapper
from langfuse.callback import CallbackHandler

load_dotenv()

def create_simple_chain():
    """Create a simple LangChain chain (same as previous example)"""
    
    # Create components
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful assistant. Answer the following question: {question}"
    )
    
    output_parser = StrOutputParser()
    
    # Create chain
    chain = prompt | llm | output_parser
    
    return chain

def main():
    """Test the chain with Langfuse observability"""
    # Initialize Langfuse callback handler in main with env vars
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    chain = create_simple_chain()
    
    # Invoke with callbacks
    response = chain.invoke(
        {"question": "What is the capital of France?"}, 
        config={"callbacks": [langfuse_handler]}
    )
    
    print(f"Response: {response}")
    print("✅ Check your Langfuse dashboard for traces!")

if __name__ == "__main__":
    main()
```

### Step 6: Run and Explore Dashboard
1. Run your application: `python langchain_demo.py`
2. Go to your Langfuse dashboard at [cloud.langfuse.com](https://cloud.langfuse.com)
3. Navigate to "Traces" to see your application execution
4. Click on a trace to explore:
   - Input/output for each step
   - Token usage and costs
   - Latency metrics
   - Model parameters

## Part 3: Advanced Tracing with Session Management

### Step 7: Add Session and User Tracking
Create `advanced_tracing.py` for more sophisticated observability:

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langfuse.callback import CallbackHandler
import uuid

load_dotenv()

def create_conversation_chain():
    """Create a conversational chain with memory simulation"""
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant having a conversation.
        
        Previous context: {context}
        User question: {question}
        
        Provide a helpful response that considers the conversation context."""
    )
    
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    
    return chain

def simulate_conversation():
    """Simulate a multi-turn conversation with proper session tracking"""
    
    # Create session ID for tracking conversation
    session_id = str(uuid.uuid4())
    user_id = "demo_user"
    
    # Initialize chain
    chain = create_conversation_chain()
    
    # Create Langfuse handler once as singleton with env vars
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        session_id=session_id,
        user_id=user_id
    )
    
    # Conversation context
    conversation_context = ""
    
    # Sample conversation turns
    conversation_turns = [
        "Hello, I'm planning a trip to Japan. Any recommendations?",
        "What's the best time of year to visit?", 
        "What about food recommendations?",
        "How much should I budget for this trip?"
    ]
    
    for i, question in enumerate(conversation_turns):
        print(f"\n--- Turn {i+1} ---")
        print(f"User: {question}")
        
        # Invoke chain with tracing (reusing same handler)
        response = chain.invoke(
            {
                "context": conversation_context,
                "question": question
            },
            config={
                "callbacks": [langfuse_handler],
                "run_name": f"conversation_turn_{i+1}",
                "metadata": {
                    "turn": i+1,
                    "conversation_topic": "Japan travel planning"
                }
            }
        )
        
        print(f"Assistant: {response}")
        
        # Update context for next turn
        conversation_context += f"User: {question}\nAssistant: {response}\n"
    
    print(f"\n✅ Conversation complete! Session ID: {session_id}")
    print("Check your Langfuse dashboard for the full conversation trace.")

if __name__ == "__main__":
    simulate_conversation()
```

### Step 8: Explore Session Analytics
1. Run the conversation: `python advanced_tracing.py`
2. In Langfuse dashboard, go to "Sessions" to see conversation-level analytics
3. Click on your session to explore:
   - Multi-turn conversation flow
   - Total tokens and costs for the session
   - User journey patterns
   - Conversation quality metrics

## Part 4: Dashboard Analysis and Insights

### Understanding the Langfuse Interface

**Key Dashboard Sections:**
- **Traces**: Individual LLM calls and their execution details
- **Sessions**: Grouped conversations or user interactions  
- **Users**: User-level analytics and behavior patterns
- **Models**: Performance comparison across different models
- **Analytics**: Cost analysis, token usage trends, latency metrics

### Analytics Deep Dive

1. **Performance Monitoring**:
   - Track response times across different chains
   - Identify bottlenecks in complex workflows
   - Monitor token usage patterns and costs

2. **Quality Assessment**:
   - Review input/output pairs for quality
   - Identify common failure patterns
   - Track conversation flow effectiveness

3. **Cost Management**:
   - Monitor API costs across different models
   - Optimize based on token usage patterns
   - Set up cost alerts and budgets

## Part 5: Production Best Practices

### Environment Configuration

For production deployments:

```python
# production_config.py
import os
from langfuse.callback import CallbackHandler

# Global variable to store singleton handler
_langfuse_handler = None

def get_langfuse_handler():
    """Singleton Langfuse handler - finds or creates the handler"""
    global _langfuse_handler
    
    if _langfuse_handler is None:
        try:
            _langfuse_handler = CallbackHandler(
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"), 
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
        except Exception as e:
            print(f"Langfuse setup failed: {e}")
            return None
    
    return _langfuse_handler
```

### Key Recommendations

1. **Always use environment variables** for API keys
2. **Add error handling** for Langfuse initialization failures
3. **Use session IDs** to group related interactions
4. **Add meaningful metadata** for better analytics
5. **Monitor costs regularly** using Langfuse analytics
6. **Set up alerts** for unusual usage patterns

## Next Steps

- Explore Langfuse evaluation features for quality scoring
- Set up automated evaluation pipelines
- Integrate with your existing monitoring infrastructure
- Consider self-hosting Langfuse for sensitive applications

## Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [LangChain Integration Guide](https://langfuse.com/docs/integrations/langchain)
- [Observability Best Practices](https://langfuse.com/docs/tracing)

---

You now have comprehensive observability for your LangChain applications! Use these insights to optimize performance, manage costs, and improve user experience.